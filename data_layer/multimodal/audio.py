import os
import subprocess
from functools import lru_cache
from faster_whisper import WhisperModel


# -----------------------------------------------------------
# Load Whisper Model Once (Medium = best balance for Malayalam)
# -----------------------------------------------------------
@lru_cache(maxsize=1)
def load_model():
    return WhisperModel(
        model_size_or_path="large-v2",
        device="cpu",
        compute_type="int8"   # Faster on CPU
    )


# -----------------------------------------------------------
# Clean & Normalize Audio (Critical for Accuracy)
# -----------------------------------------------------------
def clean_audio(input_path: str) -> str:
    output_path = "temp_clean_audio.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    return output_path


# -----------------------------------------------------------
# Main Transcription Function
# -----------------------------------------------------------
def transcribe_audio(file_path: str) -> str:
    """
    Stable Malayalam + Mixed English transcription.
    Offline.
    No API dependency.
    """

    model = load_model()

    # Step 1: Clean audio
    cleaned_file = clean_audio(file_path)

    try:
        # Step 2: Transcribe (force Malayalam base language)
        segments, info = model.transcribe(
            cleaned_file,
            beam_size=5      # Improves decoding accuracy
        )

        transcript_parts = []

        for segment in segments:
            transcript_parts.append(segment.text.strip())

        transcript = " ".join(transcript_parts).strip()

    finally:
        # Step 3: Cleanup temp file
        if os.path.exists(cleaned_file):
            os.remove(cleaned_file)

    return transcript