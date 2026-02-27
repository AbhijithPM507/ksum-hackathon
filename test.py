from data_layer.multimodal.audio import transcribe_audio

text = transcribe_audio("call1.mp4")

print("\nTranscript:\n")
print(text)