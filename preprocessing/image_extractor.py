import cv2
import easyocr
import pytesseract
from PIL import Image
import numpy as np

# Initialize EasyOCR once
reader = easyocr.Reader(['en', 'ml'], gpu=False)

def preprocess_image(image_path: str):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return gray

def extract_printed_text(image_path: str) -> str:
    img = preprocess_image(image_path)
    text = pytesseract.image_to_string(img, lang="eng+mal")
    return text.strip()

def extract_handwritten_text(image_path: str) -> str:
    results = reader.readtext(image_path)
    text = " ".join([r[1] for r in results])
    return text.strip()

def extract_text_from_image(image_path: str) -> str:
    """
    Hybrid OCR approach:
    Try printed OCR first, fallback to EasyOCR if text too short.
    """
    printed_text = extract_printed_text(image_path)

    if len(printed_text) > 20:
        return printed_text

    # fallback for handwritten
    return extract_handwritten_text(image_path)