from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class ComplaintCreate(BaseModel):
    message: str
    location: Optional[str] = None
    department: Optional[str] = None


class Complaint(BaseModel):
    complaint_id: str
    message: str
    location: Optional[str]
    department: Optional[str]
    category: str
    severity: str
    risk_score: int
    action_priority: str
    created_at: datetime

    @staticmethod
    def create(data: ComplaintCreate, ai_result: dict):
        return Complaint(
            complaint_id=str(uuid.uuid4()),
            message=data.message,
            location=data.location,
            department=data.department,
            category=ai_result["category"],
            severity=ai_result["severity"],
            risk_score=ai_result["risk_score"],
            action_priority=ai_result["action_priority"],
            created_at=datetime.utcnow()
        )