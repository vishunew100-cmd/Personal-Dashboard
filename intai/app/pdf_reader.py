import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF.
    Falls back to OCR if page has little or no text.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    extracted_text = []

    for page_index, page in enumerate(doc):
        text = page.get_text("text").strip()

        # If meaningful text exists, use it
        if text and len(text) > 50:
            extracted_text.append(text)
            continue

        # OCR fallback
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        ocr_text = pytesseract.image_to_string(img)

        extracted_text.append(ocr_text)
    return "\n\n".join(extracted_text)
