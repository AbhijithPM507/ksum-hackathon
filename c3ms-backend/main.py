import os
import shutil
from fastapi import FastAPI, UploadFile, File
from models import ComplaintCreate, Complaint
from storage import (
    add_complaint,
    get_all_complaints,
    get_complaint_count,
    get_last_hash
)
from ai_engine import analyze_complaint
from blockchain import create_block
from media_engine import transcribe_audio

app = FastAPI(
    title="C3MS AI + Blockchain + Media Engine",
    version="4.0.0"
)

UPLOAD_FOLDER = "temp_audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"status": "C3MS Full Engine Running 🚀"}


# -----------------------------
# TEXT COMPLAINT
# -----------------------------
@app.post("/complaint")
def create_complaint(data: ComplaintCreate):
    ai_result = analyze_complaint(data.message)

    complaint_data = {
        "message": data.message,
        "location": data.location,
        "department": data.department,
        "category": ai_result["category"],
        "risk_score": ai_result["risk_score"]
    }

    previous_hash = get_last_hash()
    block = create_block(complaint_data, previous_hash)

    complaint = Complaint.create(data, ai_result, block)
    add_complaint(complaint)

    return {
        "complaint_id": complaint.complaint_id,
        "category": complaint.category,
        "severity": complaint.severity,
        "risk_score": complaint.risk_score,
        "block_hash": complaint.block_hash
    }


# -----------------------------
# AUDIO COMPLAINT (VOICE NOTE ENGINE)
# -----------------------------
@app.post("/voice-complaint")
async def voice_complaint(
    file: UploadFile = File(...),
    location: str = None,
    department: str = None
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe audio
    transcript = transcribe_audio(file_path)

    # Process transcript via AI engine
    ai_result = analyze_complaint(transcript)

    complaint_data = {
        "message": transcript,
        "location": location,
        "department": department,
        "category": ai_result["category"],
        "risk_score": ai_result["risk_score"]
    }

    previous_hash = get_last_hash()
    block = create_block(complaint_data, previous_hash)

    complaint_obj = Complaint.create(
        ComplaintCreate(
            message=transcript,
            location=location,
            department=department
        ),
        ai_result,
        block
    )

    add_complaint(complaint_obj)

    os.remove(file_path)

    return {
        "transcript": transcript,
        "category": complaint_obj.category,
        "severity": complaint_obj.severity,
        "risk_score": complaint_obj.risk_score,
        "block_hash": complaint_obj.block_hash
    }


# -----------------------------
# GET ALL COMPLAINTS
# -----------------------------
@app.get("/complaints")
def list_complaints():
    return get_all_complaints()


# -----------------------------
# ANALYTICS
# -----------------------------
@app.get("/analytics")
def analytics():
    complaints = get_all_complaints()

    category_count = {}
    high_risk = 0

    for c in complaints:
        category_count[c.category] = category_count.get(c.category, 0) + 1
        if c.severity == "High":
            high_risk += 1

    return {
        "total_complaints": len(complaints),
        "high_risk_cases": high_risk,
        "category_distribution": category_count
    }