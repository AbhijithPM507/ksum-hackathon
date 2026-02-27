import re
import spacy

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

def redact_pii(text: str) -> str:
    redacted_text = text

    # ---- Regex Redactions ----

    # Phone numbers (10 digit Indian format)
    redacted_text = re.sub(r"\b\d{10}\b", "[REDACTED_PHONE]", redacted_text)

    # Email addresses
    redacted_text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        redacted_text
    )

    # Aadhaar (12 digits)
    redacted_text = re.sub(r"\b\d{12}\b", "[REDACTED_AADHAAR]", redacted_text)

    # ---- Named Entity Redaction (Names, Locations) ----
    doc = nlp(redacted_text)

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "GPE", "LOC"]:
            redacted_text = redacted_text.replace(ent.text, "[REDACTED]")

    return redacted_text