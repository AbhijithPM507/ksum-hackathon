import sys
import os
sys.path.append(os.path.abspath("."))

from backend.logic.service import process_complaint

complaint = "Officer demanded 5000 rupees for issuing land certificate."

result = process_complaint(complaint)

print("\n===== FINAL RESULT =====\n")
print(result)