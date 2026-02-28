import cv2
import easyocr
import pytesseract
import numpy as np
from PIL import Image

# Explicit path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize EasyOCR once
reader = easyocr.Reader(['en'], gpu=False)


# -----------------------------
# IMAGE PREPROCESSING
# -----------------------------
def preprocess_image(image_path: str):
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Invalid image path or unreadable image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold improves OCR accuracy
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh


# -----------------------------
# PRINTED TEXT (TESSERACT)
# -----------------------------
def extract_printed_text(image_path: str) -> str:
    img = preprocess_image(image_path)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(
        img,
        lang="eng+mal",
        config=custom_config
    )

    return text.strip()


# -----------------------------
# HANDWRITTEN TEXT (EASYOCR)
# -----------------------------
def extract_handwritten_text(image_path: str) -> str:
    results = reader.readtext(image_path)

    # Only extract high-confidence detections
    text = " ".join([r[1] for r in results if r[2] > 0.4])

    return text.strip()


# -----------------------------
# HYBRID PIPELINE
# -----------------------------
def extract_text_from_image(image_path: str) -> str:
    """
    Hybrid OCR pipeline:
    1. Try Tesseract for printed text
    2. If weak result, fallback to EasyOCR
    """

    try:
        printed_text = extract_printed_text(image_path)

        # If sufficient text found → assume printed
        if len(printed_text) > 30:
            return printed_text

    except Exception:
        pass

    # Fallback for handwriting or noisy scans
    handwritten_text = extract_handwritten_text(image_path)

    return handwritten_text