from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import tempfile
import os
from .image_extractor import extract_text_from_image

def extract_text_from_pdf(pdf_path: str) -> str:

    reader = PdfReader(pdf_path)
    text_content = ""

    # First try direct text extraction
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_content += extracted

    # If text found → return
    if len(text_content.strip()) > 50:
        return text_content.strip()

    # Otherwise assume scanned PDF → convert to images
    images = convert_from_path(pdf_path)

    combined_text = ""

    for img in images:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            img.save(tmp.name)
            combined_text += extract_text_from_image(tmp.name)
            os.unlink(tmp.name)

    return combined_text.strip()