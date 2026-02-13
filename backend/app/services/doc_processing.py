import os
from importlib import import_module
from typing import Iterable, List, Optional, Tuple


SUPPORTED_TEXT_EXTS = {'.txt', '.md'}
SUPPORTED_DOC_EXTS = SUPPORTED_TEXT_EXTS | {'.pdf'}


class UnsupportedDocumentTypeError(ValueError):
    pass


def _load_pdf_reader():
    """Load PdfReader from available PDF libs.

    Tries modern `pypdf` first, then legacy-compatible `PyPDF2`.
    """
    candidates = ('pypdf', 'PyPDF2')
    for module_name in candidates:
        try:
            module = import_module(module_name)
            reader = getattr(module, 'PdfReader', None)
            if reader:
                return reader
        except Exception:
            continue

    raise UnsupportedDocumentTypeError(
        'PDF parser dependency missing: please install pypdf (or PyPDF2). '
        'Run: pip install -r requirements.txt'
    )


def _read_pdf_pages(path: str, max_chars: int = 2_000_000) -> List[Tuple[int, str]]:
    """Extract text by page from PDF and preserve page number metadata."""
    PdfReader = _load_pdf_reader()

    try:
        reader = PdfReader(path)
    except Exception as e:
        raise UnsupportedDocumentTypeError(f'Failed to read PDF: {e}') from e

    pages: list[tuple[int, str]] = []
    total = 0

    for idx, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or '').strip()
        if not page_text:
            continue

        left = max_chars - total
        if left <= 0:
            break

        if len(page_text) > left:
            page_text = page_text[:left]

        pages.append((idx, page_text))
        total += len(page_text)

    return pages


def simple_read_text(path: str, max_chars: int = 2_000_000) -> str:
    """Read text from supported document types (.txt/.md/.pdf)."""
    ext = os.path.splitext(path)[1].lower()

    if ext in SUPPORTED_TEXT_EXTS:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(max_chars)

    if ext == '.pdf':
        pages = _read_pdf_pages(path, max_chars=max_chars)
        return '\n'.join(t for _, t in pages)

    raise UnsupportedDocumentTypeError(
        f'Unsupported document type: {ext or "unknown"}. '
        f'Please upload one of: {", ".join(sorted(SUPPORTED_DOC_EXTS))}'
    )


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80) -> Iterable[str]:
    """Simple sliding-window chunker (character-based)."""
    text = ' '.join(text.split())
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


def extract_document_chunks(path: str, max_chars: int = 2_000_000) -> List[Tuple[Optional[int], str]]:
    """Extract chunk list with optional page metadata for supported file types."""
    ext = os.path.splitext(path)[1].lower()

    if ext in SUPPORTED_TEXT_EXTS:
        text = simple_read_text(path, max_chars=max_chars)
        return [(None, ch) for ch in chunk_text(text)]

    if ext == '.pdf':
        all_chunks: list[tuple[Optional[int], str]] = []
        pages = _read_pdf_pages(path, max_chars=max_chars)
        for page_no, page_text in pages:
            for ch in chunk_text(page_text):
                all_chunks.append((page_no, ch))
        return all_chunks

    raise UnsupportedDocumentTypeError(
        f'Unsupported document type: {ext or "unknown"}. '
        f'Please upload one of: {", ".join(sorted(SUPPORTED_DOC_EXTS))}'
    )