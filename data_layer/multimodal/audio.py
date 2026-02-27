import os
import tempfile
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

SCRIBE_MODEL = "scribe_v2"


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using ElevenLabs Scribe (SDK).
    Returns speaker-labeled transcript.
    """

    eleven_api_key = os.getenv("ELEVENLABS_API_KEY")

    if not eleven_api_key:
        raise ValueError("ELEVENLABS_API_KEY not configured in .env")

    el_client = ElevenLabs(api_key=eleven_api_key)

    # ElevenLabs expects file object
    with open(file_path, "rb") as audio_file:
        response = el_client.speech_to_text.convert(
            file=audio_file,
            model_id=SCRIBE_MODEL,
            tag_audio_events=True,
            diarize=True
        )

    # Build speaker-labeled transcript
    lines = []
    current_speaker = None
    current_line = ""

    for word in response.words:
        if word.speaker_id != current_speaker:
            if current_line:
                lines.append(f"Speaker {current_speaker}: {current_line.strip()}")
            current_speaker = word.speaker_id
            current_line = word.text
        else:
            current_line += f" {word.text}"

    if current_line:
        lines.append(f"Speaker {current_speaker}: {current_line.strip()}")

    return "\n".join(lines)