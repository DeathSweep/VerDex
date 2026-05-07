import os
import fitz  # PyMuPDF

from translateParser import extract_blocks
from translationEngine import translate


def rebuild_translated_pdf(input_pdf_path, output_pdf_path=None):
    """
    Reads a PDF, translates text blocks,
    rebuilds a translated PDF with PyMuPDF,
    and returns the output path.
    """

    # -----------------------------
    # Output filename
    # -----------------------------
    if output_pdf_path is None:
        base_name = os.path.basename(input_pdf_path)
        output_pdf_path = os.path.join(
            os.path.dirname(input_pdf_path),
            f"translated_{base_name}"
        )

    # -----------------------------
    # Extract blocks from parser
    # -----------------------------
    blocks = extract_blocks(input_pdf_path)

    # -----------------------------
    # Open original PDF
    # -----------------------------
    original_doc = fitz.open(input_pdf_path)

    # -----------------------------
    # Create translated PDF
    # -----------------------------
    translated_doc = fitz.open()

    # -----------------------------
    # Process each page
    # -----------------------------
    for page_num in range(len(original_doc)):

        original_page = original_doc[page_num]

        # Preserve page size
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

        # Get blocks for current page
        page_blocks = [
            b for b in blocks
            if b["page"] == page_num
        ]

        for block in page_blocks:

            x0, y0, x1, y1 = block["bbox"]
            original_text = block["text"].strip()

            if not original_text:
                continue

            try:

                # -----------------------------
                # Translate text
                # -----------------------------
                translated_text = translate(original_text)

                # -----------------------------
                # Insert translated text
                # -----------------------------
                new_page.insert_textbox(
                    fitz.Rect(x0, y0, x1, y1),
                    translated_text,
                    fontsize=11,
                    fontname="helv",
                    color=(0, 0, 0),
                    align=0
                )

            except Exception as e:
                print(f"Error translating block: {e}")

    # -----------------------------
    # Save PDF
    # -----------------------------
    translated_doc.save(output_pdf_path)

    translated_doc.close()
    original_doc.close()

    return output_pdf_path