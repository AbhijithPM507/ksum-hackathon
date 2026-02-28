from fastapi import FastAPI, Request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from data_layer.storage.database import init_db
from data_layer.storage.database import save_complaint
from data_layer.storage.database import get_complaint_by_id

import os
from dotenv import load_dotenv

from backend.logic.service import process_complaint
from preprocessing.media_pipeline import extract_text_from_media


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

app = FastAPI()


# -----------------------------
# STARTUP
# -----------------------------
@app.on_event("startup")
def startup():
    init_db()
    os.makedirs("uploads", exist_ok=True)


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=1)


def error_handler(update, context):
    print("Unhandled error:", context.error)


dispatcher.add_error_handler(error_handler)


# -----------------------------
# CONVERSATION STATES
# -----------------------------
CHOOSING_FORMAT, WAITING_INPUT = range(2)


# -----------------------------
# START COMMAND
# -----------------------------
def start(update, context):
    keyboard = [["Text"], ["Image"], ["PDF"], ["Voice"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    update.message.reply_text(
        """
Welcome to Kerala Corruption Reporting Bot.

Please include in your complaint:

• Official Name (if known)
• Position / Designation
• Place / Office Location (MANDATORY)
• Description of incident

You may write naturally.

How would you like to submit your complaint?
""",
        reply_markup=reply_markup
    )

    return CHOOSING_FORMAT


# -----------------------------
# FORMAT SELECTION
# -----------------------------
def choose_format(update, context):
    selected = update.message.text

    if selected not in ["Text", "Image", "PDF", "Voice"]:
        update.message.reply_text("Please choose a valid option.")
        return CHOOSING_FORMAT

    context.user_data["format"] = selected

    if selected == "Text":
        update.message.reply_text("Please type your complaint now.")
    elif selected == "Voice":
        update.message.reply_text("Please send your voice message now.")
    else:
        update.message.reply_text(f"Please upload your {selected} file now.")

    return WAITING_INPUT


# -----------------------------
# TRACK COMMAND
# -----------------------------
def track_command(update, context):
    if not context.args:
        update.message.reply_text("Usage: /track <complaint_id>")
        return

    complaint_id = context.args[0]
    complaint = get_complaint_by_id(complaint_id)

    if not complaint:
        update.message.reply_text("Complaint not found.")
        return

    reply = f"""
📄 Complaint Status

ID: {complaint['id']}
Category: {complaint['category']}
Risk: {complaint['risk_level']}
Status: {complaint['status']}
Submitted: {complaint['timestamp']}
Integrity Verified: ✅
"""

    if complaint["escalation_required"]:
        reply += f"\n⚠ Escalated At: {complaint['escalation_timestamp']}"

    update.message.reply_text(reply)


# -----------------------------
# HANDLE COMPLAINT INPUT
# -----------------------------
def handle_input(update, context):
    selected_format = context.user_data.get("format")
    extracted_text = None

    # TEXT INPUT
    if selected_format == "Text" and update.message.text:
        extracted_text = update.message.text

    # IMAGE INPUT
    elif selected_format == "Image" and update.message.photo:
        file = update.message.photo[-1].get_file()
        file_path = f"uploads/{update.message.message_id}.jpg"
        file.download(file_path)

        try:
            extracted_text = extract_text_from_media(file_path)
        except Exception as e:
            print("OCR Error:", e)
            update.message.reply_text("Could not process the image.")
            return ConversationHandler.END

    # PDF INPUT
    elif selected_format == "PDF" and update.message.document:
        file = update.message.document.get_file()
        file_path = f"uploads/{update.message.document.file_name}"
        file.download(file_path)

        try:
            extracted_text = extract_text_from_media(file_path)
        except Exception as e:
            print("PDF Error:", e)
            update.message.reply_text("Could not process the PDF.")
            return ConversationHandler.END

    # VOICE INPUT
    elif selected_format == "Voice" and update.message.voice:
        file = update.message.voice.get_file()
        file_path = f"uploads/{update.message.message_id}.ogg"
        file.download(file_path)

        try:
            extracted_text = extract_text_from_media(file_path)
        except Exception as e:
            print("Audio Transcription Error:", e)
            update.message.reply_text("Could not process the voice message.")
            return ConversationHandler.END

    else:
        update.message.reply_text("Invalid format. Please restart using /start.")
        return ConversationHandler.END

    # -----------------------------
    # BASIC VALIDATION
    # -----------------------------
    if not extracted_text or len(extracted_text.strip()) < 15:
        update.message.reply_text(
            "Complaint details are insufficient. Please provide more information."
        )
        return ConversationHandler.END

    update.message.reply_text("Processing your complaint...")

    # -----------------------------
    # PROCESS COMPLAINT
    # -----------------------------
    result = process_complaint(extracted_text)

    save_complaint(result)

    # -----------------------------
    # ESCALATION ALERT
    # -----------------------------
    if result["risk_level"] == "High" and ADMIN_CHAT_ID:
        bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"""
🚨 HIGH RISK CORRUPTION ALERT

ID: {result['complaint_id']}
Category: {result['category']}
Risk: {result['risk_level']}

Immediate review recommended.
"""
        )

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    reply = f"""
✅ Complaint Registered

ID: {result['complaint_id']}
Category: {result['category']}
Risk Level: {result['risk_level']}
Integrity: {result['integrity_status']}
"""

    update.message.reply_text(reply)

    return ConversationHandler.END


# -----------------------------
# CONVERSATION HANDLER
# -----------------------------
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING_FORMAT: [MessageHandler(Filters.text, choose_format)],
        WAITING_INPUT: [
            MessageHandler(
                Filters.text | Filters.photo | Filters.document | Filters.voice,
                handle_input
            )
        ],
    },
    fallbacks=[],
)

dispatcher.add_handler(conv_handler)
dispatcher.add_handler(CommandHandler("track", track_command))

from data_layer.storage.database import DB_PATH
import sqlite3


@app.get("/complaints")
def get_all_complaints():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]
# -----------------------------
# TELEGRAM WEBHOOK
# -----------------------------
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return {"status": "ok"}