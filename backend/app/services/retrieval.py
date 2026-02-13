import re
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Chunk, Document


def _tokenize(s: str) -> set[str]:
    s = (s or '').lower()
    tokens = re.findall(r'[a-zA-Z0-9\u4e00-\u9fff]+', s)
    return set(t for t in tokens if len(t) >= 2)


def _make_snippet(text: str, q_tokens: set[str], max_len: int = 420) -> str:
    text = text or ''
    if not text:
        return ''

    hit_pos: Optional[int] = None
    for t in sorted(q_tokens, key=len, reverse=True):
        p = text.lower().find(t.lower())
        if p != -1:
            hit_pos = p
            break

    if hit_pos is None:
        snippet = text[:max_len]
        if len(text) > max_len:
            snippet += '…'
        return snippet

    half = max_len // 2
    start = max(0, hit_pos - half)
    end = min(len(text), start + max_len)

    boundary = max(text.rfind('。', 0, start), text.rfind('\n', 0, start))
    if boundary != -1 and boundary < start:
        start = boundary + 1

    snippet = text[start:end].strip()

    if start > 0:
        snippet = '…' + snippet
    if end < len(text):
        snippet += '…'

    return snippet


def retrieve_chunks(db: Session, question: str, owner_id: int, top_k: int = 6) -> List[Dict]:
    """Retrieve evidence chunks only from current user's indexed documents."""
    question = (question or '').strip()
    q_tokens = _tokenize(question)
    if not q_tokens:
        q_tokens = set(re.findall(r'\S+', question.lower()))

    rows: List[Tuple[Chunk, Document]] = (
        db.query(Chunk, Document)
        .join(Document, Document.id == Chunk.document_id)
        .filter(Document.owner_id == owner_id, Document.status == 'indexed')
        .order_by(Chunk.id.desc())
        .limit(800)
        .all()
    )
    if not rows:
        return []

    scored: List[Tuple[int, Chunk, Document]] = []
    for ch, doc in rows:
        c_tokens = _tokenize(ch.text or '')
        score = len(q_tokens & c_tokens)
        scored.append((score, ch, doc))

    scored.sort(key=lambda x: (x[0], x[1].id), reverse=True)

    k = max(1, int(top_k))
    best = [(ch, doc) for sc, ch, doc in scored if sc > 0][:k]
    if not best:
        best = [(ch, doc) for _, ch, doc in scored[:k]]

    return [
        {
            'chunk_id': ch.id,
            'page': ch.page,
            'source_name': doc.name,
            'snippet': _make_snippet(ch.text or '', q_tokens, max_len=420),
            'text': ch.text or '',
        }
        for ch, doc in best
    ]