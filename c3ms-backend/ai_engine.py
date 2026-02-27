def analyze_complaint(message: str) -> dict:
    text = message.lower()
    risk_score = 0

    # Category Detection
    if any(word in text for word in ["bribe", "money", "rupees", "payment", "cash"]):
        category = "Bribery"
        risk_score += 3
    elif any(word in text for word in ["delay", "pending", "not approved", "file not moving"]):
        category = "Service Delay"
        risk_score += 2
    elif any(word in text for word in ["favor", "relative", "nepotism"]):
        category = "Favoritism"
        risk_score += 3
    elif any(word in text for word in ["tender", "contract", "bid"]):
        category = "Tender Manipulation"
        risk_score += 4
    elif any(word in text for word in ["land scam", "property fraud"]):
        category = "Land Scam"
        risk_score += 4
    else:
        category = "General Corruption"
        risk_score += 1

    # Additional Risk Factors
    if any(word in text for word in ["5000", "10000", "amount", "lakhs"]):
        risk_score += 2

    if any(word in text for word in ["threat", "harassment", "intimidation"]):
        risk_score += 3

    if any(word in text for word in ["collector", "officer", "department", "government"]):
        risk_score += 2

    # Severity Levels
    if risk_score <= 3:
        severity = "Low"
        action = "Monitor"
    elif 4 <= risk_score <= 6:
        severity = "Medium"
        action = "Review Required"
    else:
        severity = "High"
        action = "Immediate Investigation"

    return {
        "category": category,
        "risk_score": risk_score,
        "severity": severity,
        "action_priority": action
    }