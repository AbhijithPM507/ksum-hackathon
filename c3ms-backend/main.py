import os
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
    return {"status": "Telegram Multimedia Engine Running 🚀"}

# -----------------------------
# TELEGRAM WEBHOOK
# -----------------------------
@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    print("\n=== TELEGRAM UPDATE RECEIVED ===")
    print(data)

    if "message" not in data:
        return {"status": "ignored"}

    message = data["message"]
    chat_id = message["chat"]["id"]

    # TEXT MESSAGE
    if "text" in message:
        text = message["text"]
        print("📝 Text received:", text)
        send_telegram_message(chat_id, "✅ Complaint received successfully.")

    # VOICE MESSAGE
    elif "voice" in message:
        file_id = message["voice"]["file_id"]
        file_url = get_file_url(file_id)

        print("🎙 Voice file URL:", file_url)
        send_telegram_message(chat_id, "✅ Voice complaint received successfully.")

    # AUDIO FILE
    elif "audio" in message:
        file_id = message["audio"]["file_id"]
        file_url = get_file_url(file_id)

        print("🎧 Audio file URL:", file_url)
        send_telegram_message(chat_id, "✅ Audio complaint received successfully.")

    # PHOTO
    elif "photo" in message:
        file_id = message["photo"][-1]["file_id"]  # highest resolution
        file_url = get_file_url(file_id)

        print("📷 Photo file URL:", file_url)
        send_telegram_message(chat_id, "✅ Photo evidence received successfully.")

    # DOCUMENT
    elif "document" in message:
        file_id = message["document"]["file_id"]
        file_url = get_file_url(file_id)

        print("📎 Document file URL:", file_url)
        send_telegram_message(chat_id, "✅ Document received successfully.")

    else:
        send_telegram_message(
            chat_id,
            "⚠ Unsupported format. Please send text, voice, photo, or document."
        )

    return {"status": "ok"}

# -----------------------------
# GET FILE URL FROM TELEGRAM
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