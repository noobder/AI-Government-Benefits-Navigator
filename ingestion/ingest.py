"""Ingestion pipeline entry point.

Reads documents under ingestion/documents/<category>/, extracts text,
cleans + chunks it, attaches metadata, and indexes it into the vector store
used by the running backend.

Usage:
    python ingest.py

Note: the backend's main scheme data (data/seed_schemes.json) is the source
of truth for eligibility rules, documents, and official URLs — this pipeline
is for indexing *supplementary* narrative government documents (guidelines,
FAQs, notifications) placed under ingestion/documents/ so the chat assistant
can cite richer context. It never invents scheme facts on its own.
"""
from __future__ import annotations

import os

from chunk import clean_text, chunk_text
from parse import extract_text
from index import index_chunks

DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")


def run() -> None:
    total_chunks = 0
    for category in sorted(os.listdir(DOCUMENTS_DIR)):
        category_dir = os.path.join(DOCUMENTS_DIR, category)
        if not os.path.isdir(category_dir):
            continue
        for filename in sorted(os.listdir(category_dir)):
            path = os.path.join(category_dir, filename)
            if not os.path.isfile(path):
                continue
            try:
                raw_text = extract_text(path)
            except NotImplementedError as e:
                print(f"Skipping {path}: {e}")
                continue

            cleaned = clean_text(raw_text)
            chunks = chunk_text(cleaned)
            chunks_with_metadata = [
                (
                    chunk,
                    {
                        "category": category,
                        "document_name": filename,
                        "source": "supplementary_document",
                        "section": f"chunk_{i}",
                    },
                )
                for i, chunk in enumerate(chunks)
            ]
            count = index_chunks(chunks_with_metadata)
            total_chunks += count
            print(f"Indexed {count} chunks from {path}")

    print(f"Done. Total chunks indexed: {total_chunks}")


if __name__ == "__main__":
    run()
