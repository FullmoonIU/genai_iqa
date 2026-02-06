import os
from typing import Iterable


def simple_read_text(path: str, max_chars: int = 200_000) -> str:
    """MVP: only reads plain text-like files.

    For pdf/docx, you can later swap in proper parsers.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in {".txt", ".md"}:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    # Placeholder for pdf/docx: just return filename prompt
    return f"[Placeholder] ... update parsers for {ext}. File: {os.path.basename(path)}\n"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> Iterable[str]:
    """Very simple sliding-window chunker (characters).

    Later you can switch to paragraph/heading-aware chunking.
    """
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
        i += max(1, chunk_size - overlap)
    return chunks
    # Placeholder for pdf/doc/docx parsing
    return (
        f"[PLACEHOLDER PARSER] File type {ext} not parsed in MVP. "
        "Please convert to .txt/.md for now, or implement pdf/docx parsing later.\n"
        f"File: {os.path.basename(path)}"
    )


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> Iterable[str]:
    text = " ".join(text.split())
    if not text:
        return []

    chunks: list[str] = []
    i = 0
    while i < len(text):
        end = min(len(text), i + chunk_size)
        chunks.append(text[i:end])
        if end == len(text):
            break
        i = max(0, end - overlap)
    return chunks
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks
