import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    client = OpenAI(api_key=api_key)

    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return transcript.text