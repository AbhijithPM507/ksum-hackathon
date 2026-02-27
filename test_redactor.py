from data_layer.pii_redactor.redactor import redact_pii

text = "My name is Rahul Kumar and officer demanded 5000 rupees."

result = redact_pii(text)

print("Redacted Text:")
print(result)