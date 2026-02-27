from backend.logic.graph_builder import build_graph
from data_layer.processor import process_complaint as data_processor
import uuid

graph = build_graph()

def process_complaint(complaint_text: str):

    complaint_id = str(uuid.uuid4())

    # For now, mock blockchain values (later member3 should manage internally)
    previous_hash = "0"
    total_blocks = 1

    # 🔹 Call Data Layer Processor FIRST
    data_payload = data_processor(
        complaint_id=complaint_id,
        original_text=complaint_text,
        previous_hash=previous_hash,
        total_blocks=total_blocks
    )

    # 🔹 Now call LLM logic using redacted text + legal context
    state = {
        "complaint_text": data_payload["redacted_text"],
        "retrieved_docs": data_payload["legal_context"]
    }

    result = graph.invoke(state)

    # Attach blockchain metadata to final output
    result["complaint_id"] = complaint_id
    result["data_hash"] = data_payload["data_hash"]
    result["timestamp"] = data_payload["timestamp"]
    result["integrity_status"] = data_payload["integrity_status"]

    return result