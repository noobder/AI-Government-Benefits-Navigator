"""Speech provider abstraction.

For the hackathon MVP, the primary voice path runs entirely in the browser
via the Web Speech API (SpeechRecognition for STT, SpeechSynthesis for TTS),
which needs no backend and already supports English and Tamil in Chromium
browsers. These server-side endpoints exist so a real cloud speech provider
can be plugged in later without changing the frontend contract — until then
they report unavailable so the frontend falls back to the browser API.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from app.config import get_settings


class SpeechProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language: str) -> str: ...

    @abstractmethod
    def synthesize(self, text: str, language: str) -> bytes: ...

    @abstractmethod
    def is_available(self) -> bool: ...


class MockSpeechProvider(SpeechProvider):
    def transcribe(self, audio_bytes: bytes, language: str) -> str:
        raise RuntimeError("Server-side speech-to-text is not configured. Use the browser voice fallback.")

    def synthesize(self, text: str, language: str) -> bytes:
        raise RuntimeError("Server-side text-to-speech is not configured. Use the browser voice fallback.")

    def is_available(self) -> bool:
        return False


class CloudSpeechProvider(SpeechProvider):
    """Placeholder for a real cloud STT/TTS integration (e.g. Google/Azure)."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def transcribe(self, audio_bytes: bytes, language: str) -> str:
        raise NotImplementedError("Wire up a real cloud speech-to-text provider here.")

    def synthesize(self, text: str, language: str) -> bytes:
        raise NotImplementedError("Wire up a real cloud text-to-speech provider here.")

    def is_available(self) -> bool:
        return True


def get_speech_provider() -> SpeechProvider:
    settings = get_settings()
    if settings.speech_to_text_api_key:
        return CloudSpeechProvider(settings.speech_to_text_api_key)
    return MockSpeechProvider()
