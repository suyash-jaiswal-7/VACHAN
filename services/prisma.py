
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PRISMA_URL = "https://api.vachana.ai/stt/v3"


def transcribe_audio(audio_bytes, filename, language_code="indic-auto", api_key=None):
    api_key = api_key or os.getenv("GNANI_API_KEY")

    if not api_key:
        raise ValueError("Gnani API key is not configured.")

    if not audio_bytes:
        raise ValueError("No audio file received.")

    headers = {
        "X-API-Key-ID": api_key
    }

    files = {
        "audio_file": (
            filename,
            audio_bytes,
            "application/octet-stream"
        )
    }

    data = {
        "model": "prisma-v3.0",
        "language_code": language_code,
        "format": "codemix"
    }

    response = requests.post(
        PRISMA_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=90
    )

    try:
        result = response.json()
    except ValueError:
        raise RuntimeError("Invalid response received from Gnani.")

    if not response.ok:
        raise RuntimeError(
            f"Gnani API error ({response.status_code}): {result}"
        )

    if not result.get("success"):
        raise RuntimeError(f"Transcription failed: {result}")

    return {
        "transcript": result.get("transcript", ""),
        "detected_language": result.get("detected_language_code"),
        "request_id": result.get("request_id")
    }
