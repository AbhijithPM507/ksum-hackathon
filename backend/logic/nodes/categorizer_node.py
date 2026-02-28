import json
import re

from data_layer.pii_redactor.redactor import redact_pii
from backend.logic.llm_wrapper import generate_response


def categorize_node(state):
    """
    Categorizes complaint into corruption type and assigns severity score.
    Applies selective PII redaction while preserving official identity and place.
    """

    text = state.get("complaint_text", "")

    if not text:
        state["category"] = "Other"
        state["severity_score"] = 0.5
        return state

    # -------------------------------------------------
    # Extract Official Name and Place (if structured)
    # -------------------------------------------------

    name_match = re.search(r"Official Name:\s*(.*)", text, re.IGNORECASE)
    place_match = re.search(r"Place:\s*(.*)", text, re.IGNORECASE)

    official_name = name_match.group(1).strip() if name_match else ""
    place = place_match.group(1).strip() if place_match else ""

    # Remove empty values from protected list
    protected = [x for x in [official_name, place] if x]

    # -------------------------------------------------
    # Selective PII Redaction
    # -------------------------------------------------

    try:
        clean_text = redact_pii(text, protected_entities=protected)
    except Exception as e:
        print("Redaction Error:", e)
        clean_text = text  # fallback to original

    state["complaint_text"] = clean_text

    # -------------------------------------------------
    # LLM Classification Prompt
    # -------------------------------------------------

    prompt = f"""
Classify this corruption complaint into:
[Bribery, Service Delay, Favoritism, Fraud, Other]

Also assign severity score from 0 to 1.

Complaint:
{clean_text}

Return JSON only:
{{
  "category": "",
  "severity_score": 0.0
}}
"""

    try:
        response = generate_response(prompt)
    except Exception as e:
        print("LLM Error:", e)
        state["category"] = "Other"
        state["severity_score"] = 0.5
        return state

    # -------------------------------------------------
    # Extract JSON from LLM response safely
    # -------------------------------------------------

    json_match = re.search(r"\{.*\}", response, re.DOTALL)

    if json_match:
        try:
            result = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            result = {
                "category": "Other",
                "severity_score": 0.5
            }
    else:
        result = {
            "category": "Other",
            "severity_score": 0.5
        }

    # -------------------------------------------------
    # Update State
    # -------------------------------------------------

    state["category"] = result.get("category", "Other")
    state["severity_score"] = float(result.get("severity_score", 0.5))

    return state