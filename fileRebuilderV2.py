import os
import html
import fitz
import pdfplumber

from translateEngine import (
    translate,
    load_translation_model,
    unload_translation_model
)


# =========================================================
# CONFIG
# =========================================================

FONT_NAME = "malayalam"
FONT_FILE = "NotoSansMalayalam-Regular.ttf"

DEFAULT_LINE_HEIGHT = 1
MIN_FONT_SIZE = 8
PARAGRAPH_GAP_THRESHOLD = 4
PAGE_MARGIN = 40
TABLE_LINE_WIDTH = 0.7


# =========================================================
# UTILITIES
# =========================================================


def sanitize_text(text):
    return html.escape(text.strip())


# =========================================================
# TABLE DETECTION
# =========================================================


def detect_tables(pdf_path):

    tables_by_page = {}

    with pdfplumber.open(pdf_path) as pdf:

        for page_index, page in enumerate(pdf.pages):

            extracted_tables = page.extract_tables()

            page_tables = []

            for table in extracted_tables:

                processed_rows = []

                for row in table:

                    if row:
                        processed_rows.append([
                            cell if cell else ""
                            for cell in row
                        ])

                if processed_rows:
                    page_tables.append(processed_rows)

            tables_by_page[page_index] = page_tables

    return tables_by_page


# =========================================================
# PARAGRAPH EXTRACTION
# =========================================================


def extract_paragraphs(page):

    page_dict = page.get_text("dict")

    paragraphs = []

    current_paragraph = None

    previous_y = None

    for block in page_dict["blocks"]:

        if block["type"] != 0:
            continue

        for line in block["lines"]:

            spans = line["spans"]

            if not spans:
                continue

            line_text = ""

            line_bbox = [
                min(span["bbox"][0] for span in spans),
                min(span["bbox"][1] for span in spans),
                max(span["bbox"][2] for span in spans),
                max(span["bbox"][3] for span in spans),
            ]

            first_span = spans[0]

            for span in spans:
                text = span["text"]

                if text:
                    line_text += text

            line_text = line_text.strip()

            if not line_text:
                continue

            current_y = line_bbox[1]

            # -------------------------------------------------
            # PARAGRAPH GROUPING
            # -------------------------------------------------

            same_paragraph = False

            if previous_y is not None:

                vertical_gap = abs(current_y - previous_y)

                if vertical_gap < PARAGRAPH_GAP_THRESHOLD:
                    same_paragraph = True

            if same_paragraph and current_paragraph:

                current_paragraph["text"] += " " + line_text

                current_paragraph["bbox"][0] = min(
                    current_paragraph["bbox"][0],
                    line_bbox[0]
                )

                current_paragraph["bbox"][1] = min(
                    current_paragraph["bbox"][1],
                    line_bbox[1]
                )

                current_paragraph["bbox"][2] = max(
                    current_paragraph["bbox"][2],
                    line_bbox[2]
                )

                current_paragraph["bbox"][3] = max(
                    current_paragraph["bbox"][3],
                    line_bbox[3]
                )

            else:

                current_paragraph = {
                    "text": line_text,
                    "bbox": line_bbox,
                    "font": first_span["font"],
                    "size": max(first_span["size"], MIN_FONT_SIZE),
                    "flags": first_span["flags"],
                    "color": first_span["color"]
                }

                paragraphs.append(current_paragraph)

            previous_y = current_y

    return paragraphs


# =========================================================
# HTML GENERATOR
# =========================================================


def build_html(text, font_size):

    text = sanitize_text(text)

    html_content = f"""
    <style>

    @font-face {{
        font-family: {FONT_NAME};
        src: url({FONT_FILE});
    }}

    body {{
        font-family: {FONT_NAME};
        font-size: {font_size}pt;
        line-height: {DEFAULT_LINE_HEIGHT};
        color: black;
    }}

    p {{
        margin: 0;
        padding: 0;
    }}

    </style>

    <body>
        <p>{text}</p>
    </body>
    """

    return html_content


# =========================================================
# HEIGHT ESTIMATION
# =========================================================


def estimate_height(text, width, font_size):

    if width <= 0:
        return font_size * 2

    avg_char_width = font_size * 0.5

    chars_per_line = max(int(width / avg_char_width), 1)

    estimated_lines = (len(text) // chars_per_line) + 1

    line_height = font_size * DEFAULT_LINE_HEIGHT

    return estimated_lines * line_height + 10


# =========================================================
# TABLE RENDERING
# =========================================================


def render_table(page, table_data, start_y, page_width):

    if not table_data:
        return start_y

    cols = max(len(row) for row in table_data)

    table_width = page_width - (PAGE_MARGIN * 2)

    cell_width = table_width / cols

    current_y = start_y

    for row in table_data:

        translated_cells = []

        max_height = 0

        for cell in row:

            translated = translate(cell)

            translated_cells.append(translated)

            cell_height = estimate_height(
                translated,
                cell_width,
                10
            )

            max_height = max(max_height, cell_height)

        current_x = PAGE_MARGIN

        for cell_text in translated_cells:

            rect = fitz.Rect(
                current_x,
                current_y,
                current_x + cell_width,
                current_y + max_height
            )

            page.draw_rect(
                rect,
                color=(0, 0, 0),
                width=TABLE_LINE_WIDTH
            )

            html_content = build_html(cell_text, 10)

            page.insert_htmlbox(
                rect,
                html_content,
                archive=fitz.Archive("fonts")
            )

            current_x += cell_width

        current_y += max_height

    return current_y + 15


# =========================================================
# MAIN REBUILDER
# =========================================================


def rebuild_pdf(input_pdf_path, output_pdf_path=None):

    load_translation_model()

    if output_pdf_path is None:

        base = os.path.basename(input_pdf_path)

        output_pdf_path = os.path.join(
            os.path.dirname(input_pdf_path),
            f"translated_{base}"
        )

    # ---------------------------------------------
    # OPEN ORIGINAL PDF DIRECTLY
    # ---------------------------------------------

    doc = fitz.open(input_pdf_path)

    archive = fitz.Archive("fonts")

    # ---------------------------------------------
    # PROCESS PAGES
    # ---------------------------------------------

    for page_index in range(len(doc)):

        page = doc[page_index]

        paragraphs = extract_paragraphs(page)

        # -----------------------------------------
        # REPLACE TEXT BLOCK-BY-BLOCK
        # -----------------------------------------

        for paragraph in paragraphs:

            original_text = paragraph["text"]

            translated_text = translate(original_text)

            rect = fitz.Rect(paragraph["bbox"])

            font_size = paragraph["size"]

            # -------------------------------------
            # WHITE OUT ORIGINAL TEXT
            # -------------------------------------

            page.draw_rect(
                rect,
                color=(1, 1, 1),
                fill=(1, 1, 1)
            )

            # -------------------------------------
            # BUILD HTML
            # -------------------------------------

            html_content = build_html(
                translated_text,
                font_size
            )

            # -------------------------------------
            # INSERT INSIDE ORIGINAL RECT
            # -------------------------------------

            result = page.insert_htmlbox(
                rect,
                html_content,
                archive=archive,
                scale_low=0.7
            )

            # -------------------------------------
            # HANDLE OVERFLOW
            # -------------------------------------

            if isinstance(result, tuple):
                spare_height = result[0]
            else:
                spare_height = result

            # Negative means overflow
            if spare_height < 0:

                extra_height = abs(spare_height) + 5

                expanded_rect = fitz.Rect(
                    rect.x0,
                    rect.y0,
                    rect.x1,
                    rect.y1 + extra_height
                )

                # Clear larger area
                page.draw_rect(
                    expanded_rect,
                    color=(1, 1, 1),
                    fill=(1, 1, 1)
                )

                # Retry insertion
                page.insert_htmlbox(
                    expanded_rect,
                    html_content,
                    archive=archive,
                    scale_low=0.7
                )
        print(f"[PAGE {page_index + 1} Done!]")

    # ---------------------------------------------
    # SAVE
    # ---------------------------------------------

    doc.save(output_pdf_path)

    unload_translation_model()

    doc.close()

    print("\n=================================")
    print("Translated PDF saved at:")
    print(output_pdf_path)

    return output_pdf_path

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    INPUT_FILE = "input.pdf"

    rebuild_pdf(INPUT_FILE)