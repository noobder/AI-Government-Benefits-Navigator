"""Thin wrapper over app.i18n.strings, kept as a stable service-layer import
so callers (graph/workflow.py etc.) don't need to know about the i18n module
layout. All actual phrase data lives in app/i18n/strings.py.
"""
from __future__ import annotations

from app.i18n.strings import PHRASES, SUPPORTED_LANGUAGES, is_supported, translate


def translate_phrase(key: str, language: str = "en", **kwargs) -> str:
    return translate(key, language, PHRASES, **kwargs)


__all__ = ["translate_phrase", "is_supported", "SUPPORTED_LANGUAGES"]
