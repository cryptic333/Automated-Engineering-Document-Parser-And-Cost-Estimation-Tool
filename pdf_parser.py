# pdf_parser.py
import pdfplumber
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes the raw bytes of a PDF and returns all the text inside it.
    We go page by page and stitch all text together.
    """
    pages_text = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(f"\n--- Page {page_num} ---\n{text}")

    return "\n".join(pages_text)
