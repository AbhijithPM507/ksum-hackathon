import re
import spacy
from typing import List

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")


def redact_pii(text: str, protected_entities: List[str] = None) -> str:
    """
    Redacts sensitive PII from text while preserving protected entities
    like official names and office locations.

    protected_entities: list of strings that must NOT be redacted
    """

    if protected_entities is None:
        protected_entities = []

    redacted_text = text

    # ----------------------------
    # Regex-Based Redactions
    # ----------------------------

    # Phone numbers (10-digit Indian)
    redacted_text = re.sub(r"\b\d{10}\b", "[REDACTED_PHONE]", redacted_text)

    # Email addresses
    redacted_text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        redacted_text
    )

    # Aadhaar (12 digits)
    redacted_text = re.sub(r"\b\d{12}\b", "[REDACTED_AADHAAR]", redacted_text)

    # ----------------------------
    # Protect Official Entities
    # ----------------------------

    placeholder_map = {}

    for i, entity in enumerate(protected_entities):
        placeholder = f"__PROTECTED_{i}__"
        placeholder_map[placeholder] = entity
        redacted_text = redacted_text.replace(entity, placeholder)

    # ----------------------------
    # Named Entity Redaction
    # ----------------------------

    doc = nlp(redacted_text)

    for ent in doc.ents:
        if ent.label_ in ["PERSON"]:
            redacted_text = redacted_text.replace(ent.text, "[REDACTED_PERSON]")

        # NOTE:
        # We DO NOT redact GPE or LOC anymore.
        # Because location is governance-critical.

    # ----------------------------
    # Restore Protected Entities
    # ----------------------------

    for placeholder, original in placeholder_map.items():
        redacted_text = redacted_text.replace(placeholder, original)

    return redacted_text