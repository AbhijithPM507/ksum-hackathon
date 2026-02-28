import os
import subprocess
from functools import lru_cache
from faster_whisper import WhisperModel


# -----------------------------------------------------------
# Load Whisper Model Once (CPU Optimized)
# -----------------------------------------------------------
@lru_cache(maxsize=1)
def load_model():
    print(":small_blue_diamond: Using CPU (large-v2) for transcription")
    return WhisperModel(
        "large-v2",
        device="cpu",
        compute_type="int8"   # Best balance for CPU speed + memory
    )


# -----------------------------------------------------------
# Clean Audio to Optimal Format (Very Important)
# -----------------------------------------------------------
def clean_audio(input_path: str) -> str:
    """
    Converts audio to:
    - 16kHz
    - Mono
    - 16-bit PCM WAV
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Audio file not found: {input_path}")

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

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return output_path


# -----------------------------------------------------------
# Main Transcription Function
# -----------------------------------------------------------
def transcribe_audio(file_path: str) -> str:
    """
    High-accuracy Malayalam + mixed English transcription.
    Fully offline.
    CPU optimized.
    """

    model = load_model()

    cleaned_file = clean_audio(file_path)

    try:
        segments, info = model.transcribe(
            cleaned_file,
            beam_size=5
        )

        transcript_parts = []

        for segment in segments:
            transcript_parts.append(segment.text.strip())

        transcript = " ".join(transcript_parts).strip()

    finally:
        if os.path.exists(cleaned_file):
            os.remove(cleaned_file)

    return transcript