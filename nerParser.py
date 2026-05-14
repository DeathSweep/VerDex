import fitz
import pytesseract
from PIL import Image
import io

# =========================================================
# TEXT CLEANER
# =========================================================

def clean_text(text):

    # Remove excessive spaces
    text = " ".join(text.split())

    # Remove repeated newlines
    text = text.replace("\n\n", "\n")

    return text.strip()

# =========================================================
# OCR FALLBACK
# =========================================================

def run_ocr(page):

    pix = page.get_pixmap(dpi=300)

    img_bytes = pix.tobytes("png")

    image = Image.open(io.BytesIO(img_bytes))

    ocr_text = pytesseract.image_to_string(
        image,
        lang="eng+mal"
    )

    return ocr_text

# =========================================================
# MAIN PARSER
# =========================================================

def extract_text(pdf_path):

    print("Entered NER file parser.")

    doc = fitz.open(pdf_path)

    extracted_blocks = []

    for page_num, page in enumerate(doc):

        print(f"Processing page {page_num + 1}")

        # ---------------------------------------------
        # BLOCK EXTRACTION
        # ---------------------------------------------

        blocks = page.get_text("blocks")

        page_text = ""

        for block in blocks:

            block_text = block[4].strip()

            if not block_text:
                continue

            page_text += block_text + "\n"

        # ---------------------------------------------
        # OCR FALLBACK
        # ---------------------------------------------

        if len(page_text.strip()) < 50:

            print("Low text detected. Running OCR...")

            page_text = run_ocr(page)

        # ---------------------------------------------
        # CLEAN TEXT
        # ---------------------------------------------

        page_text = clean_text(page_text)

        extracted_blocks.append({
            "page": page_num + 1,
            "text": page_text
        })

    print("File successfully parsed.")

    return extracted_blocks