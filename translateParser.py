import fitz  # PyMuPDF

def extract_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    structured_data = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")

        for b in blocks:
            x0, y0, x1, y1, text, *_ = b

            if text.strip():
                structured_data.append({
                    "page": page_num,
                    "bbox": (x0, y0, x1, y1),
                    "text": text
                })

    return structured_data