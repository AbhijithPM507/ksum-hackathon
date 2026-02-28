import json
from backend.logic.llm_wrapper import generate_response
import re
def risk_analysis_node(state):

    prompt = f"""
    You are an anti-corruption AI investigator.

    Complaint:
    {state['complaint_text']}

    Category:
    {state['category']}

    Legal Context:
    {state['retrieved_docs']}

    Return JSON only:
    {{
      "risk_level": "Low/Medium/High",
      "recommended_action": "",
      "relevant_laws": []
    }}
    """

    response = generate_response(prompt)

    # Extract JSON block safely


    json_match = re.search(r"\{.*\}", response, re.DOTALL)

    if json_match:
        json_text = json_match.group(0)
        result = json.loads(json_text)
    else:
        # fallback if model fails
        result = {
            "risk_level": "Medium",
            "recommended_action": "Manual review required.",
            "relevant_laws": []
        }

    state["risk_level"] = result["risk_level"]
    state["recommended_action"] = result["recommended_action"]
    state["relevant_laws"] = result["relevant_laws"]

    state["escalation_required"] = True if state["severity_score"] > 0.8 else False

    return state