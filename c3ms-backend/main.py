import os
from fastapi import FastAPI
from dotenv import load_dotenv
from models import ComplaintCreate, Complaint
from storage import add_complaint, get_all_complaints, get_complaint_count
from ai_engine import analyze_complaint

load_dotenv()

app = FastAPI(
    title="C3MS AI Core Engine",
    version="2.0.0"
)

# -----------------------------
# Root
# -----------------------------
@app.get("/")
def root():
    return {"status": "C3MS AI Engine Running 🚀"}


# -----------------------------
# Create Complaint with AI
# -----------------------------
@app.post("/complaint")
def create_complaint(data: ComplaintCreate):
    ai_result = analyze_complaint(data.message)

    complaint = Complaint.create(data, ai_result)
    add_complaint(complaint)

    return {
        "status": "Complaint registered",
        "complaint_id": complaint.complaint_id,
        "category": complaint.category,
        "severity": complaint.severity,
        "risk_score": complaint.risk_score,
        "action_priority": complaint.action_priority
    }


# -----------------------------
# Get All Complaints
# -----------------------------
@app.get("/complaints")
def list_complaints():
    return get_all_complaints()


# -----------------------------
# Analytics Endpoint
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