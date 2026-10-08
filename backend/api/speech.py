from io import BytesIO

import edge_tts
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


router = APIRouter(prefix="/speech", tags=["Speech"])


LANGUAGE_VOICES = {
    "en": "en-IN-NeerjaNeural",
    "en-IN": "en-IN-NeerjaNeural",
    "ta": "ta-IN-PallaviNeural",
    "ta-IN": "ta-IN-PallaviNeural",
    "te": "te-IN-ShrutiNeural",
    "te-IN": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "kn": "kn-IN-SapnaNeural",
    "kn-IN": "kn-IN-SapnaNeural",
}


class TTSRequest(BaseModel):
    text: str
    language: str = "en-IN"


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text is required.",
        )

    voice = LANGUAGE_VOICES.get(request.language)

    if not voice:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {request.language}. "
                f"Supported languages: en, ta, te, hi, kn."
            ),
        )

    try:
        audio_buffer = BytesIO()

        communicate = edge_tts.Communicate(
            text,
            voice,
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_buffer.seek(0)

        if audio_buffer.getbuffer().nbytes == 0:
            raise RuntimeError(
                "Edge TTS returned no audio data."
            )

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="speech.mp3"',
                "Cache-Control": "no-cache",
            },
        )

    except HTTPException:
        raise

    except Exception as exc:
        print(
            f"TTS generation failed "
            f"(voice={voice}, language={request.language}): {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate speech.",
        )