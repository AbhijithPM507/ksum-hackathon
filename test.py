from data_layer.multimodal.audio import transcribe_audio

text = transcribe_audio("call.ogg")

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Saved to output.txt")