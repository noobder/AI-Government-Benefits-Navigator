"""Extract raw text from a scheme source document.

For the hackathon MVP, source documents are plain text/markdown files placed
under ingestion/documents/<category>/. Extend `extract_text` to handle PDFs
(e.g. with pypdf) or HTML government pages without changing callers.
"""
from __future__ import annotations

import os


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    raise NotImplementedError(f"No extractor registered for '{ext}' files yet. Add one in parse.py.")
