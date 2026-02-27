from typing import List
from models import Complaint

complaints_db: List[Complaint] = []
blockchain_chain: List[str] = []


def add_complaint(complaint: Complaint):
    complaints_db.append(complaint)
    blockchain_chain.append(complaint.block_hash)


def get_all_complaints() -> List[Complaint]:
    return complaints_db


def get_complaint_count() -> int:
    return len(complaints_db)


def get_last_hash() -> str:
    if not blockchain_chain:
        return "0"
    return blockchain_chain[-1]