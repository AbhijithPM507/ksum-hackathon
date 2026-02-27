from data_layer.processor import process_complaint

# Simulated DB values
previous_hash = "0"
total_blocks = 0

sample_complaint = """
My name is Rajesh Kumar from Kollam.
Officer Ramesh demanded 5000 rupees for approval.
My phone number is 9876543210.
"""

result = process_complaint(
    complaint_id="CMP_TEST_001",
    original_text=sample_complaint,
    previous_hash=previous_hash,
    total_blocks=total_blocks
)

print("\n===== FULL PIPELINE RESULT =====\n")
print("Complaint ID:", result["complaint_id"])
print("Redacted Text:\n", result["redacted_text"])
print("Hash:", result["data_hash"])
print("Previous Hash:", result["previous_hash"])
print("Timestamp:", result["timestamp"])
print("\nLegal Context Returned:\n")

for i, ctx in enumerate(result["legal_context"], 1):
    print(f"\nContext {i}:\n{ctx[:300]}...")