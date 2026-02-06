# app/services/qa.py
from typing import Any, Dict, List, Tuple

from app.services.llm import build_llm_answer


def build_answer(question: str, evidences: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """
    统一入口：
    - 优先调用大模型（llm.py）
    - 如果失败 → fallback 到规则回答
    """

    try:
        answer, citations = build_llm_answer(question, evidences)

        if answer and answer.strip():
            return answer, citations

    except Exception as e:
        # fallback
        fallback, citations = build_stub_answer(question, evidences)
        fallback += f"\n\n（提示：大模型失败，已回退规则回答：{type(e).__name__}）"
        return fallback, citations

    # 万一 llm 返回空
    return build_stub_answer(question, evidences)


# -----------------------------
# fallback 规则回答（保底）
# -----------------------------
def build_stub_answer(question: str, evidences: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:

    if not evidences:
        return "未检索到相关资料片段，无法回答。", []

    ev = evidences[0]
    snippet = ev.get("snippet") or ""

    answer = f"根据资料：\n{snippet[:400]}"
    citations = []

    for ev in evidences:
        citations.append({
            "source_name": ev.get("source_name"),
            "page": ev.get("page"),
            "chunk_id": ev.get("chunk_id"),
            "snippet": (ev.get("snippet") or "")[:200],
        })

    return answer, citations
