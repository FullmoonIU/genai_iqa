import re
from typing import Dict, List, Set, Tuple

from app.core.config import settings

_REF_PATTERN = re.compile(r'\[(\d+)\]')


def _extract_used_ref_indexes(answer: str, max_ref: int) -> List[int]:
    """Extract de-duplicated evidence indexes like [1][2] from answer text."""
    if not answer:
        return []

    seen: Set[int] = set()
    ordered: List[int] = []

    for m in _REF_PATTERN.finditer(answer):
        idx = int(m.group(1))
        if 1 <= idx <= max_ref and idx not in seen:
            seen.add(idx)
            ordered.append(idx)

    return ordered


def _build_precise_citations(answer: str, evidences: List[Dict]) -> List[Dict]:
    """Build citations only for evidence actually used in answer.

    Strategy:
    1) parse [n] markers;
    2) fallback to fuzzy snippet-head matching;
    3) fallback to one citation only (first evidence).
    """
    if not evidences:
        return []

    used_indexes = _extract_used_ref_indexes(answer, max_ref=len(evidences))

    if not used_indexes:
        answer_norm = (answer or '').lower()
        for i, ev in enumerate(evidences, start=1):
            snippet = (ev.get('snippet') or '').strip()
            if not snippet:
                continue
            probe = snippet[:40].lower()
            if probe and probe in answer_norm:
                used_indexes.append(i)

    if not used_indexes:
        used_indexes = [1]

    citations: List[Dict] = []
    for idx in used_indexes:
        ev = evidences[idx - 1]
        citations.append(
            {
                'source_name': ev.get('source_name'),
                'page': ev.get('page'),
                'chunk_id': ev.get('chunk_id'),
                'snippet': (ev.get('snippet') or '')[:200],
                'text': ev.get('text'),
            }
        )

    return citations


def build_llm_answer(question: str, evidences: List[Dict]) -> Tuple[str, List[Dict]]:
    """LLM answer with precise citations mapped from model-used evidence."""
    if not settings.ZHIPU_API_KEY:
        raise RuntimeError('ZHIPU_API_KEY is not configured')

    from zhipuai import ZhipuAI

    client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)

    context_lines = []
    for i, ev in enumerate(evidences, start=1):
        src = ev.get('source_name', 'unknown')
        page = ev.get('page', None)
        snippet = ev.get('snippet', '') or ''
        context_lines.append(f'[{i}] 来源: {src} 页码: {page}\n{snippet}')

    context = '\n\n'.join(context_lines).strip()

    system = (
        '你是一个严谨的学习助手。你只能基于【给定资料片段】回答，不要编造。'
        '如果资料不足以回答，请明确说“资料不足”，并说明缺少什么信息。'
        '你必须在结论和关键论断后使用 [编号] 标注证据来源，编号只能来自给定片段。'
    )

    user = f"""【问题】
{question}

【给定资料片段】
{context}

【要求】
1) 先给出简洁结论（1-2句）
2) 再给出条理化解释（分点）
3) 每个关键论断都加上证据编号 [1][2]...
4) 回答末尾给出“引用”列表，列出你实际使用过的片段编号
"""

    resp = client.chat.completions.create(
        model=settings.ZHIPU_MODEL,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        temperature=0.2,
    )

    answer = resp.choices[0].message.content.strip()
    citations = _build_precise_citations(answer, evidences)
    return answer, citations