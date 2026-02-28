import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "complaints.db")


# -------------------------------------------------
# INIT DATABASE
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id TEXT PRIMARY KEY,

            official_name TEXT,
            position TEXT,
            place TEXT,
            description TEXT,

            category TEXT,
            risk_level TEXT,
            severity_score REAL,

            timestamp TEXT,
            integrity_hash TEXT,
            evidence_hash TEXT,

            escalation_required BOOLEAN,
            escalation_timestamp TEXT,

            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# SAVE COMPLAINT
# -------------------------------------------------
def save_complaint(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    escalation_required = data["risk_level"] == "High"
    escalation_timestamp = datetime.utcnow().isoformat() if escalation_required else None

    cursor.execute("""
        INSERT INTO complaints (
            id,
            official_name,
            position,
            place,
            description,

            category,
            risk_level,
            severity_score,

            timestamp,
            integrity_hash,
            evidence_hash,

            escalation_required,
            escalation_timestamp,
            status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("complaint_id"),

        data.get("official_name"),
        data.get("position"),
        data.get("place"),
        data.get("description"),

        data.get("category"),
        data.get("risk_level"),
        data.get("severity_score"),

        data.get("timestamp"),
        data.get("data_hash"),
        data.get("evidence_hash"),

        escalation_required,
        escalation_timestamp,
        "Escalated" if escalation_required else "Submitted"
    ))

    conn.commit()
    conn.close()


# -------------------------------------------------
# GET COMPLAINT BY ID
# -------------------------------------------------
def get_complaint_by_id(complaint_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            "id": row[0],
            "official_name": row[1],
            "position": row[2],
            "place": row[3],
            "description": row[4],

            "category": row[5],
            "risk_level": row[6],
            "severity_score": row[7],

            "timestamp": row[8],
            "integrity_hash": row[9],
            "evidence_hash": row[10],

            "escalation_required": bool(row[11]),
            "escalation_timestamp": row[12],
            "status": row[13],
        }

    return None