from data_layer.pii_redactor.redactor import redact_pii

sample_text = """
My name is Rajesh Kumar from Kollam.
My phone number is 9876543210.
My email is rajesh@gmail.com.
Officer Ramesh demanded 5000 rupees.
"""

result = redact_pii(sample_text)

print(result)