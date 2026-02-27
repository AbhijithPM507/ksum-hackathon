import os
from .image_extractor import extract_text_from_image
from .pdf_extractor import extract_text_from_pdf
from .audio_transcriber import transcribe_audio

def extract_text_from_media(file_path: str) -> str:

    extension = os.path.splitext(file_path)[1].lower()

    if extension in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    elif extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension in [".mp3", ".wav", ".m4a"]:
        return transcribe_audio(file_path)

    else:
        raise ValueError("Unsupported file type")