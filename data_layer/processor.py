from typing import Dict

# 🔐 PII
from data_layer.pii_redactor.redactor import redact_pii

# 🔗 Blockchain
from data_layer.blockchain.process_integrity import process_integrity

# 🧠 Legal Vector DB Query
from data_layer.vector_db.query import query_legal_context


def process_complaint(
    complaint_id: str,
    original_text: str,
    previous_hash: str,
    total_blocks: int
) -> Dict:
    """
    Correct RAG + Integrity Pipeline

    1️⃣ Redact PII
    2️⃣ Generate Blockchain Integrity Block
    3️⃣ Retrieve Legal Context from Vector DB
    4️⃣ Return structured response for LLM layer
    """

    # -------------------------------------------------
    # 1️⃣ PII REDACTION
    # -------------------------------------------------
    redacted_text = redact_pii(original_text)

    # -------------------------------------------------
    # 2️⃣ BLOCKCHAIN INTEGRITY
    # -------------------------------------------------
    block = process_integrity(
        complaint_id=complaint_id,
        redacted_text=redacted_text,
        previous_hash=previous_hash,
        total_blocks=total_blocks
    )

    # -------------------------------------------------
    # 3️⃣ LEGAL CONTEXT RETRIEVAL (RAG)
    # -------------------------------------------------
    legal_context_results = query_legal_context(redacted_text)

    # Extract only text chunks
    legal_context = legal_context_results

    # -------------------------------------------------
    # 4️⃣ RETURN FOR LLM LAYER
    # -------------------------------------------------
    return {
        "complaint_id": complaint_id,
        "redacted_text": redacted_text,
        "data_hash": block["data_hash"],
        "previous_hash": block["previous_hash"],
        "timestamp": block["timestamp"],
        "legal_context": legal_context,
        "integrity_status": "secured"
    }