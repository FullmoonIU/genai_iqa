from app.services.llm import _extract_used_ref_indexes, _build_precise_citations


def test_extract_used_ref_indexes_dedup_and_range():
    out = _extract_used_ref_indexes("结论[2] 解释[2][1][99]", max_ref=3)
    assert out == [2, 1]


def test_build_precise_citations_by_refs_only():
    evidences = [
        {"source_name": "A", "page": 1, "chunk_id": 11, "snippet": "alpha"},
        {"source_name": "B", "page": 2, "chunk_id": 22, "snippet": "beta"},
        {"source_name": "C", "page": 3, "chunk_id": 33, "snippet": "gamma"},
    ]

    citations = _build_precise_citations("答案使用[3]并且补充[1]", evidences)
    assert [c["chunk_id"] for c in citations] == [33, 11]


def test_build_precise_citations_not_all_when_no_refs():
    evidences = [
        {"source_name": "A", "page": 1, "chunk_id": 11, "snippet": "alpha fragment"},
        {"source_name": "B", "page": 2, "chunk_id": 22, "snippet": "beta fragment"},
    ]

    citations = _build_precise_citations("这是答案，没有引用标记。", evidences)
    # fallback should not be full-citation strategy
    assert len(citations) == 1