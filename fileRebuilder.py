import os
import html
import fitz  # PyMuPDF

from translateParser import extract_blocks
from translateEngine import translate


def rebuild_translated_pdf(input_pdf_path, output_pdf_path=None):
    """
    Reads a PDF, translates text blocks,
    rebuilds a translated PDF with proper
    Malayalam Unicode rendering.
    """

    # -------------------------------------------------
    # Output filename
    # -------------------------------------------------
    if output_pdf_path is None:
        base_name = os.path.basename(input_pdf_path)

        output_pdf_path = os.path.join(
            os.path.dirname(input_pdf_path),
            f"translated_{base_name}"
        )

    # -------------------------------------------------
    # Extract blocks
    # -------------------------------------------------
    blocks = extract_blocks(input_pdf_path)

    # -------------------------------------------------
    # Open original PDF
    # -------------------------------------------------
    original_doc = fitz.open(input_pdf_path)

    # -------------------------------------------------
    # Create translated PDF
    # -------------------------------------------------
    translated_doc = fitz.open()

    # -------------------------------------------------
    # Font archive
    # -------------------------------------------------
    archive = fitz.Archive("fonts")

    # -------------------------------------------------
    # Process pages
    # -------------------------------------------------
    for page_num in range(len(original_doc)):

        original_page = original_doc[page_num]

        # Preserve original page size
        rect = original_page.rect

        new_page = translated_doc.new_page(
            width=rect.width,
            height=rect.height
        )

        # White page background
        new_page.draw_rect(
            rect,
            color=(1, 1, 1),
            fill=(1, 1, 1)
        )

        # Blocks for current page
        page_blocks = [
            b for b in blocks
            if b["page"] == page_num
        ]

        # -------------------------------------------------
        # Process text blocks
        # -------------------------------------------------
        for block in page_blocks:

            x0, y0, x1, y1 = block["bbox"]

            original_text = block["text"].strip()

            if not original_text:
                continue

            try:

                # -----------------------------------------
                # Translate text
                # -----------------------------------------
                translated_text = translate(original_text)

                print("\n======================")
                print("ORIGINAL:")
                print(original_text)

                print("\nTRANSLATED:")
                print(translated_text)

                # Escape HTML special chars
                translated_text = html.escape(translated_text)

                # -----------------------------------------
                # Insert translated text
                # -----------------------------------------
                html_content = f"""
                <style>
                @font-face {{
                    font-family: malayalam;
                    src: url(NotoSansMalayalam-Regular.ttf);
                }}

                div {{
                    font-family: malayalam;
                    font-size: 10pt;
                    color: black;
                    line-height: 1.2;
                }}
                </style>

                <div>
                    {translated_text}
                </div>
                """

                result = new_page.insert_htmlbox(
                    fitz.Rect(x0, y0, x1, y1),
                    html_content,
                    archive=archive
                )

                print("INSERT RESULT:", result)

            except Exception as e:
                print(f"\nERROR: {e}")

    # -------------------------------------------------
    # Save PDF
    # -------------------------------------------------
    translated_doc.save(output_pdf_path)

    translated_doc.close()
    original_doc.close()

    print("\nTranslated PDF saved at: ")
    print(output_pdf_path)

    return output_pdf_path