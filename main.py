import json
import uuid
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ✅ Correct import
from data_layer.processor import process_complaint

app = FastAPI()

STORAGE_FILE = "complaints.json"


# -----------------------------
# Load complaints
# -----------------------------
def load_complaints():
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# -----------------------------
# Save complaints
# -----------------------------
def save_complaints(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# Telegram Webhook
# -----------------------------
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    print("\n📩 Incoming Telegram Update:")
    print(json.dumps(data, indent=2))

    if "message" not in data:
        return JSONResponse(content={"status": "ignored"})

    message = data["message"]
    user_id = message["from"]["id"]
    username = message["from"].get("username", "unknown")
    text = message.get("text", "")

    if not text:
        return JSONResponse(content={"status": "no_text"})

    complaint_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    complaint = {
        "complaint_id": complaint_id,
        "user_id": user_id,
        "username": username,
        "timestamp": timestamp,
        "source": "telegram",
        "content": {
            "text": text,
            "media_type": "text",
            "media_url": None
        },
        "ai_analysis": {
            "category": None,
            "severity": None,
            "risk_score": None,
            "summary": None
        },
        "status": "received",
        "integrity": {}
    }

    # 🔹 Get previous hash if exists
    existing_complaints = load_complaints()

    if existing_complaints and "hash" in existing_complaints[-1].get("integrity", {}):
        previous_hash = existing_complaints[-1]["integrity"]["hash"]
    else:
        previous_hash = "0"

    total_blocks = len(existing_complaints) + 1

    # 🔹 Call Dev 2/3 Processor
    processed_data = process_complaint(
        complaint_id=complaint_id,
        original_text=text,
        previous_hash=previous_hash,
        total_blocks=total_blocks
    )

    # 🔹 Update complaint
    complaint["content"]["text"] = processed_data["redacted_text"]

    complaint["integrity"] = {
        "hash": processed_data["data_hash"],
        "previous_hash": processed_data["previous_hash"],
        "timestamp": processed_data["timestamp"],
        "status": processed_data["integrity_status"]
    }

    complaint["legal_context"] = processed_data["legal_context"]
    complaint["status"] = "secured"

    existing_complaints.append(complaint)
    save_complaints(existing_complaints)

    print("\n✅ Complaint Processed & Stored:")
    print(json.dumps(complaint, indent=2))

    return JSONResponse(content={"status": "received"})


# -----------------------------
# View complaints
# -----------------------------
@app.get("/complaints")
def get_complaints():
    return load_complaints()