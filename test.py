from data_layer.multimodal.audio import transcribe_audio

text = transcribe_audio("call.ogg")

print("\nTranscript:\n")
print(text)