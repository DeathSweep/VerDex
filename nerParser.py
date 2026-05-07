import fitz

def extract_text(pdf_path):
    print("Entered NER file Parser.")
    doc = fitz.open(pdf_path)

    full_text = ""

    for page in doc:
        text = page.get_text()
        full_text += text + "\n"

    print("File successfully parsed.")
    return full_text