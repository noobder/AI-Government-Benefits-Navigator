from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.services.voice_service import get_speech_provider

router = APIRouter(prefix="/api/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: str = Form("en")):
    provider = get_speech_provider()
    if not provider.is_available():
        return JSONResponse(
            status_code=200,
            content={
                "available": False,
                "message": "Server-side speech-to-text is not configured. Falling back to browser voice input.",
            },
        )
    audio_bytes = await audio.read()
    text = provider.transcribe(audio_bytes, language)
    return {"available": True, "text": text}


@router.post("/synthesize")
async def synthesize(text: str = Form(...), language: str = Form("en")):
    provider = get_speech_provider()
    if not provider.is_available():
        return JSONResponse(
            status_code=200,
            content={
                "available": False,
                "message": "Server-side text-to-speech is not configured. Falling back to browser voice output.",
            },
        )
    provider.synthesize(text, language)
    return {"available": True}
