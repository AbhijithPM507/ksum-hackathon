import os
import uuid
import json
import hashlib
import datetime
import requests
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STORAGE_FILE = "complaints.json"

# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
async def root():
    return {"status": "C3MS Complaint Engine Running 🚀"}

# -----------------------------
# TELEGRAM WEBHOOK
# -----------------------------
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" not in data:
        return {"status": "ignored"}

    message = data["message"]
    chat = message["chat"]

    user_id = chat["id"]
    username = chat.get("username", "unknown")

    text = None
    media_type = "none"
    media_url = None

    if "text" in message:
        text = message["text"]
        media_type = "text"

    elif "voice" in message:
        file_id = message["voice"]["file_id"]
        media_type = "voice"
        media_url = get_file_url(file_id)

    elif "audio" in message:
        file_id = message["audio"]["file_id"]
        media_type = "audio"
        media_url = get_file_url(file_id)

    elif "photo" in message:
        file_id = message["photo"][-1]["file_id"]
        media_type = "photo"
        media_url = get_file_url(file_id)

    elif "document" in message:
        file_id = message["document"]["file_id"]
        media_type = "document"
        media_url = get_file_url(file_id)

    complaint = build_complaint_object(
        user_id=user_id,
        username=username,
        text=text,
        media_type=media_type,
        media_url=media_url
    )

    save_complaint(complaint)

    print("\n=== SAVED COMPLAINT OBJECT ===")
    print(complaint)

    send_telegram_message(user_id, "✅ Complaint received successfully.")

    return {"status": "ok"}

# -----------------------------
# GET ALL COMPLAINTS
# -----------------------------
@app.get("/complaints")
async def get_all_complaints():
    if not os.path.exists(STORAGE_FILE):
        return []

    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)

    return data

# -----------------------------
# GET SINGLE COMPLAINT
# -----------------------------
@app.get("/complaints/{complaint_id}")
async def get_complaint(complaint_id: str):
    if not os.path.exists(STORAGE_FILE):
        raise HTTPException(status_code=404, detail="No complaints found")

    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)

    for complaint in data:
        if complaint["complaint_id"] == complaint_id:
            return complaint

    raise HTTPException(status_code=404, detail="Complaint not found")

# -----------------------------
# BUILD COMPLAINT OBJECT
# -----------------------------
def build_complaint_object(user_id, username, text, media_type, media_url):
    complaint_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()

    hash_input = (text or "") + timestamp
    complaint_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    complaint = {
        "complaint_id": complaint_id,
        "user_id": user_id,
        "username": username,
        "timestamp": timestamp,
        "source": "telegram",

        "content": {
            "text": text,
            "media_type": media_type,
            "media_url": media_url
        },

        "ai_analysis": {
            "category": None,
            "severity": None,
            "risk_score": None,
            "summary": None
        },

        "status": "received",

        "integrity": {
            "hash": complaint_hash
        }
    }

    return complaint

# -----------------------------
# SAVE TO JSON FILE
# -----------------------------
def save_complaint(complaint):
    if not os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "w") as f:
            json.dump([], f)

    with open(STORAGE_FILE, "r") as f:
        data = json.load(f)

    data.append(complaint)

    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# GET FILE URL
# -----------------------------
def get_file_url(file_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url).json()

    file_path = response["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

    return file_url

# -----------------------------
# SEND TELEGRAM MESSAGE
# -----------------------------
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    requests.post(url, json=payload)