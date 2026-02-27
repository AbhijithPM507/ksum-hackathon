from typing import List
from models import Complaint

# In-memory storage (temporary DB)
complaints_db: List[Complaint] = []


def add_complaint(complaint: Complaint):
    complaints_db.append(complaint)


def get_all_complaints() -> List[Complaint]:
    return complaints_db


def get_complaint_count() -> int:
    return len(complaints_db)