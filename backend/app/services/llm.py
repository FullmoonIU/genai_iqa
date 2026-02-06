import os
from typing import List, Dict, Tuple

from zhipuai import ZhipuAI

def build_llm_answer(question: str, evidences: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    输入：问题 + retrieve_chunks() 返回的 evidences（list[dict]，包含 snippet/source_name/page/chunk_id）
    输出：answer + citations（保持你现有 Citation 结构）
    """
    client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
    model = os.getenv("ZHIPU_MODEL", "glm-4-plus")

    # 1) 拼上下文（关键：用 snippet，不再用 text）
    context_lines = []
    for i, ev in enumerate(evidences, start=1):
        src = ev.get("source_name", "unknown")
        page = ev.get("page", None)
        snippet = ev.get("snippet", "") or ""
        context_lines.append(f"[{i}] 来源: {src} 页码: {page}\n{snippet}")

    context = "\n\n".join(context_lines).strip()

    system = (
        "你是一个严谨的学习助手。你只能基于【给定资料片段】回答，不要编造。"
        "如果资料不足以回答，请明确说“资料不足”，并说明缺少什么信息。"
    )

    user = f"""【问题】
{question}

【给定资料片段】
{context}

【要求】
1) 先给出简洁结论（1-2句）
2) 再给出条理化解释（分点）
3) 回答末尾给出“引用”列表，按 [1][2]... 标注你用到的片段编号
"""

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )

    answer = resp.choices[0].message.content.strip()

    # 2) citations：先用“全引用”的保底策略（后续可做更精准匹配）
    citations = []
    for ev in evidences:
        citations.append({
            "source_name": ev.get("source_name"),
            "page": ev.get("page"),
            "chunk_id": ev.get("chunk_id"),
            "snippet": (ev.get("snippet") or "")[:200],
        })

    return answer, citations
