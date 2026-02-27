import os
import hashlib
import datetime
import requests
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
async def root():
    return {"status": "C3MS Telegram Engine Running 🚀"}

# -----------------------------
# TELEGRAM WEBHOOK
# -----------------------------
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    print("\n=== TELEGRAM UPDATE RECEIVED ===")
    print(data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        complaint_text = data["message"].get("text", "")

        print("User complaint:", complaint_text)

        # Process complaint
        result = process_complaint(complaint_text)

        # Format response
        reply = (
            f"📌 Complaint Received\n\n"
            f"📝 Message: {result['message']}\n"
            f"📂 Category: {result['category']}\n"
            f"⚠ Severity: {result['severity']}\n"
            f"🔢 Risk Score: {result['risk_score']}/10\n"
            f"🔐 Hash ID: {result['hash'][:12]}..."
        )

        send_telegram_message(chat_id, reply)

    return {"status": "ok"}

# -----------------------------
# PROCESS COMPLAINT (AI MOCK)
# -----------------------------
def process_complaint(text: str):
    category = detect_category(text)
    severity = calculate_severity(text)
    risk_score = severity

    timestamp = datetime.datetime.utcnow().isoformat()

    hash_input = text + timestamp
    complaint_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    return {
        "message": text,
        "category": category,
        "severity": severity_label(severity),
        "risk_score": risk_score,
        "hash": complaint_hash
    }

# -----------------------------
# CATEGORY DETECTION
# -----------------------------
def detect_category(text: str):
    text = text.lower()

    if "bribe" in text or "money" in text:
        return "Bribery"
    elif "police" in text:
        return "Police Misconduct"
    elif "hospital" in text:
        return "Healthcare Corruption"
    elif "college" in text or "school" in text:
        return "Education Corruption"
    else:
        return "General Corruption"

# -----------------------------
# SEVERITY CALCULATION
# -----------------------------
def calculate_severity(text: str):
    text = text.lower()
    score = 3

    if "urgent" in text:
        score += 3
    if "threat" in text or "violence" in text:
        score += 3
    if "high amount" in text or "lakhs" in text:
        score += 2

    return min(score, 10)

def severity_label(score: int):
    if score >= 8:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"

# -----------------------------
# SEND TELEGRAM MESSAGE
# -----------------------------
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    response = requests.post(url, json=payload)
    print("Telegram API response:", response.text)