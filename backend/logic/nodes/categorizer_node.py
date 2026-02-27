import json
from data_layer.pii_redactor.redactor import redact_pii
from backend.logic.llm_wrapper import generate_response
import re
def categorize_node(state):

    # 🔐 PII Redaction (Member 3)
    clean_text = redact_pii(state["complaint_text"])
    state["complaint_text"] = clean_text

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

    response = generate_response(prompt)


    json_match = re.search(r"\{.*\}", response, re.DOTALL)

    if json_match:
        json_text = json_match.group(0)
        result = json.loads(json_text)
    else:
        result = {
            "category": "Other",
            "severity_score": 0.5
        }

    state["category"] = result["category"]
    state["severity_score"] = result["severity_score"]

    return state