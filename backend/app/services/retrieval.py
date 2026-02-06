# app/services/retrieval.py
import re
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session

from app.models import Chunk, Document


def _tokenize(s: str) -> set[str]:
    s = (s or "").lower()
    tokens = re.findall(r"[a-zA-Z0-9\u4e00-\u9fff]+", s)
    return set(t for t in tokens if len(t) >= 2)


def _make_snippet(text: str, q_tokens: set[str], max_len: int = 420) -> str:
    """
    围绕命中位置截取，避免永远从开头截断导致“依据来源”看起来不完整。
    - max_len: 依据来源展示长度（可以按你的前端体验调大/调小）
    """
    text = text or ""
    if not text:
        return ""

    # 找一个命中的 token，定位它第一次出现的位置
    hit_pos: Optional[int] = None
    hit_token: Optional[str] = None
    for t in sorted(q_tokens, key=len, reverse=True):
        p = text.lower().find(t.lower())
        if p != -1:
            hit_pos = p
            hit_token = t
            break

    # 没命中：就从头截取，但加省略号
    if hit_pos is None:
        snippet = text[:max_len]
        if len(text) > max_len:
            snippet += "…"
        return snippet

    # 命中：以命中点为中心截取
    half = max_len // 2
    start = max(0, hit_pos - half)
    end = min(len(text), start + max_len)

    # 尽量把 start 往前挪到一个更自然的边界（句号/换行）
    boundary = max(text.rfind("。", 0, start), text.rfind("\n", 0, start))
    if boundary != -1 and boundary < start:
        start = boundary + 1

    snippet = text[start:end].strip()

    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"

    return snippet


def retrieve_chunks(db: Session, question: str, top_k: int = 6) -> List[Dict]:
    question = (question or "").strip()
    q_tokens = _tokenize(question)
    if not q_tokens:
        # 兜底：至少不要直接空
        q_tokens = set(re.findall(r"\S+", question.lower()))

    # 取一批 chunk 做 MVP 检索（后续再换 BM25/向量）
    chunks: List[Chunk] = db.query(Chunk).order_by(Chunk.id.desc()).limit(800).all()
    if not chunks:
        return []

    scored: List[Tuple[int, Chunk]] = []
    for ch in chunks:
        c_tokens = _tokenize(ch.text or "")
        score = len(q_tokens & c_tokens)
        scored.append((score, ch))

    scored.sort(key=lambda x: (x[0], x[1].id), reverse=True)

    # 有命中就取命中的 top_k；没命中就取最新的 top_k（保证不空）
    best = [ch for sc, ch in scored if sc > 0][: max(1, int(top_k))]
    if not best:
        best = chunks[: min(max(1, int(top_k)), len(chunks))]

    # 文档名映射
    doc_ids = {b.document_id for b in best}
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
    doc_map = {d.id: d for d in docs}

    results: List[Dict] = []
    for b in best:
        d = doc_map.get(b.document_id)
        full_text = b.text or ""
        results.append(
            {
                "chunk_id": b.id,
                "page": b.page,
                "source_name": d.name if d else "unknown",
                # 关键：用更“自然”的 snippet
                "snippet": _make_snippet(full_text, q_tokens, max_len=420),
                # 可选：如果你后面想做“展开全文”，也可以把全文带回去（前端不展示即可）
                # "text": full_text,
            }
        )

    return results
