"""Embedding step of the ingestion pipeline.

Kept as a thin, swappable interface: the default backend app uses
KeywordVectorStore (no embeddings needed at all — see
backend/app/rag/vector_store.py). This module exists for the path where a
real embedding API key is configured; it mirrors the backend's provider
abstraction so ingestion and the running app stay consistent.
"""
from __future__ import annotations

import os


def embed_texts(texts: list[str]) -> list[list[float]] | None:
    """Return embeddings if EMBEDDING_PROVIDER/EMBEDDING_API_KEY are configured,
    otherwise None (the keyword-based retriever needs no embeddings)."""
    provider = os.environ.get("EMBEDDING_PROVIDER", "keyword")
    api_key = os.environ.get("EMBEDDING_API_KEY")

    if provider == "keyword" or not api_key:
        return None

    if provider == "openai":
        import httpx

        client = httpx.Client(
            base_url="https://api.openai.com/v1", headers={"Authorization": f"Bearer {api_key}"}
        )
        resp = client.post("/embeddings", json={"model": "text-embedding-3-small", "input": texts})
        resp.raise_for_status()
        return [item["embedding"] for item in resp.json()["data"]]

    raise NotImplementedError(f"Unknown EMBEDDING_PROVIDER '{provider}'.")
