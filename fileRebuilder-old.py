import os
import html
import fitz  # PyMuPDF

from translateEngine import translate, load_translation_model, unload_translation_model


# =========================================================
# CONFIG
# =========================================================

FONT_NAME = "malayalam"
FONT_FILE = "NotoSansMalayalam-Regular.ttf"

DEFAULT_LINE_HEIGHT = 1.2
MIN_FONT_SIZE = 8

# =========================================================
# EXTRACT STRUCTURED LAYOUT
# =========================================================

def extract_structured_blocks(pdf_path):

    doc = fitz.open(pdf_path)

    structured_pages = []

    for page_num, page in enumerate(doc):

        page_dict = page.get_text("dict")

        page_data = []

        for block in page_dict["blocks"]:

            # Skip non-text blocks
            if block["type"] != 0:
                continue

            for line in block["lines"]:

                spans_data = []

                line_text = ""

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    spans_data.append({
                        "text": text,
                        "bbox": span["bbox"],
                        "font": span["font"],
                        "size": span["size"],
                        "flags": span["flags"],
                        "color": span["color"]
                    })

                    line_text += text + " "

                if spans_data:

                    x0 = min(s["bbox"][0] for s in spans_data)
                    y0 = min(s["bbox"][1] for s in spans_data)
                    x1 = max(s["bbox"][2] for s in spans_data)
                    y1 = max(s["bbox"][3] for s in spans_data)

                    page_data.append({
                        "text": line_text.strip(),
                        "bbox": (x0, y0, x1, y1),
                        "spans": spans_data
                    })

        structured_pages.append(page_data)

    doc.close()

    return structured_pages


# =========================================================
# MAIN PDF REBUILDER
# =========================================================

def rebuild_translated_pdf(input_pdf_path, output_pdf_path=None):
    load_translation_model()

    # -----------------------------------------------------
    # Output filename
    # -----------------------------------------------------
    if output_pdf_path is None:

        base_name = os.path.basename(input_pdf_path)

        output_pdf_path = os.path.join(
            os.path.dirname(input_pdf_path),
            f"translated_{base_name}"
        )

    # -----------------------------------------------------
    # Open original PDF
    # -----------------------------------------------------
    original_doc = fitz.open(input_pdf_path)

    # -----------------------------------------------------
    # Extract structured layout
    # -----------------------------------------------------
    structured_pages = extract_structured_blocks(input_pdf_path)

    # -----------------------------------------------------
    # Create translated PDF
    # -----------------------------------------------------
    translated_doc = fitz.open()

    # -----------------------------------------------------
    # Font archive
    # -----------------------------------------------------
    archive = fitz.Archive("fonts")

    # =====================================================
    # PROCESS PAGES
    # =====================================================
    for page_num, page_lines in enumerate(structured_pages):

        original_page = original_doc[page_num]

        rect = original_page.rect

        new_page = translated_doc.new_page(
            width=rect.width,
            height=rect.height
        )

        # White background
        new_page.draw_rect(
            rect,
            color=(1, 1, 1),
            fill=(1, 1, 1)
        )

        # -------------------------------------------------
        # Dynamic vertical flow offset
        # -------------------------------------------------
        y_offset = 0

        # =================================================
        # PROCESS LINES
        # =================================================
        for line in page_lines:

            original_text = line["text"].strip()

            if not original_text:
                continue

            try:

                # -----------------------------------------
                # Translate line
                # -----------------------------------------
                translated_text = translate(original_text)

                print("\n=================================")
                print("ORIGINAL:")
                print(original_text)

                print("\nTRANSLATED:")
                print(translated_text)

                translated_text = html.escape(translated_text)

                # -----------------------------------------
                # Original bbox
                # -----------------------------------------
                x0, y0, x1, y1 = line["bbox"]

                # Apply dynamic offset
                y0 += y_offset
                y1 += y_offset

                # -----------------------------------------
                # Typography from original span
                # -----------------------------------------
                first_span = line["spans"][0]

                font_size = max(first_span["size"], MIN_FONT_SIZE)

                # Slightly larger for Malayalam readability
                font_size *= 1.05

                # -----------------------------------------
                # Initial rectangle
                # -----------------------------------------
                rect = fitz.Rect(x0, y0, x1, y1)

                # -----------------------------------------
                # HTML content
                # -----------------------------------------
                html_content = f"""
                <style>

                @font-face {{
                    font-family: {FONT_NAME};
                    src: url({FONT_FILE});
                }}

                div {{
                    font-family: {FONT_NAME};
                    font-size: {font_size}pt;
                    color: black;
                    line-height: {DEFAULT_LINE_HEIGHT};
                }}

                </style>

                <div>
                    {translated_text}
                </div>
                """

                # -----------------------------------------
                # First render attempt
                # -----------------------------------------
                result = new_page.insert_htmlbox(
                    rect,
                    html_content,
                    archive=archive,
                    scale_low=0.8
                )

                # PyMuPDF compatibility fix
                if isinstance(result, tuple):
                    spare_height = result[0]
                else:
                    spare_height = result

                # -----------------------------------------
                # If overflow occurs
                # -----------------------------------------
                if spare_height < 0:

                    overflow = abs(spare_height)

                    extra_height = overflow + 4

                    expanded_rect = fitz.Rect(
                        x0,
                        y0,
                        x1,
                        y1 + extra_height
                    )

                    # Re-render into expanded area
                    new_page.insert_htmlbox(
                        expanded_rect,
                        html_content,
                        archive=archive,
                        scale_low=0.8
                    )

                    # Push following content downward
                    y_offset += extra_height

                    print(f"Expanded by: {extra_height}")

                else:

                    print("Inserted normally")

            except Exception as e:

                print("\n=================================")
                print("ERROR:")
                print(e)

    # =====================================================
    # SAVE PDF
    # =====================================================
    translated_doc.save(output_pdf_path)
    unload_translation_model()

    translated_doc.close()
    original_doc.close()

    print("\n=================================")
    print("Translated PDF saved at:")
    print(output_pdf_path)

    return output_pdf_path