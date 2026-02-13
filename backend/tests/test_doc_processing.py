from pathlib import Path
from types import SimpleNamespace

import pytest

import app.services.doc_processing as doc_processing
from app.services.doc_processing import (
    UnsupportedDocumentTypeError,
    chunk_text,
    extract_document_chunks,
    simple_read_text,
)


class _FakePage:
    def __init__(self, text: str):
        self._text = text

    def extract_text(self):
        return self._text


class _FakeReader:
    def __init__(self, _path: str):
        self.pages = [_FakePage('第一页内容'), _FakePage('第二页内容')]


class _LongFakeReader:
    def __init__(self, _path: str):
        self.pages = [_FakePage('A' * 3000), _FakePage('B' * 3000)]


def test_simple_read_text_rejects_unsupported_ext(tmp_path: Path):
    p = tmp_path / 'a.docx'
    p.write_text('fake', encoding='utf-8')

    with pytest.raises(UnsupportedDocumentTypeError):
        simple_read_text(str(p))


def test_simple_read_text_pdf_with_pypdf(tmp_path: Path, monkeypatch):
    p = tmp_path / 'a.pdf'
    p.write_bytes(b'%PDF-1.4\n%fake')

    monkeypatch.setitem(__import__('sys').modules, 'pypdf', SimpleNamespace(PdfReader=_FakeReader))
    text = simple_read_text(str(p), max_chars=100)

    assert '第一页内容' in text
    assert '第二页内容' in text


def test_simple_read_text_pdf_fallback_to_pypdf2(tmp_path: Path, monkeypatch):
    p = tmp_path / 'a.pdf'
    p.write_bytes(b'%PDF-1.4\n%fake')

    def _fake_import(name):
        if name == 'pypdf':
            raise ImportError('missing pypdf')
        if name == 'PyPDF2':
            return SimpleNamespace(PdfReader=_FakeReader)
        raise ImportError(name)

    monkeypatch.setattr(doc_processing, 'import_module', _fake_import)
    text = simple_read_text(str(p), max_chars=100)
    assert '第一页内容' in text


def test_simple_read_text_pdf_missing_dependency(tmp_path: Path, monkeypatch):
    p = tmp_path / 'a.pdf'
    p.write_bytes(b'%PDF-1.4\n%fake')

    monkeypatch.setattr(doc_processing, 'import_module', lambda _name: (_ for _ in ()).throw(ImportError('missing')))

    with pytest.raises(UnsupportedDocumentTypeError) as ei:
        simple_read_text(str(p), max_chars=100)
    assert 'please install pypdf' in str(ei.value).lower()


def test_extract_document_chunks_pdf_keeps_page_number(tmp_path: Path, monkeypatch):
    p = tmp_path / 'a.pdf'
    p.write_bytes(b'%PDF-1.4\n%fake')

    monkeypatch.setitem(__import__('sys').modules, 'pypdf', SimpleNamespace(PdfReader=_FakeReader))
    chunks = extract_document_chunks(str(p), max_chars=2000)

    assert chunks
    assert chunks[0][0] == 1
    assert any(page_no == 2 for page_no, _ in chunks)


def test_simple_read_text_pdf_reads_beyond_old_limit(tmp_path: Path, monkeypatch):
    p = tmp_path / 'big.pdf'
    p.write_bytes(b'%PDF-1.4\n%fake')

    monkeypatch.setitem(__import__('sys').modules, 'pypdf', SimpleNamespace(PdfReader=_LongFakeReader))
    text = simple_read_text(str(p))

    assert len(text) > 200_000 or len(text) == 6001


def test_chunk_text_has_overlap():
    text = 'a' * 1000
    chunks = list(chunk_text(text, chunk_size=100, overlap=20))
    assert len(chunks) > 1
    assert chunks[0][-20:] == chunks[1][:20]