from typing import Optional

from pydantic import BaseModel


class HistoryCitation(BaseModel):
    source_name: str
    page: Optional[int] = None
    chunk_id: Optional[int] = None
    snippet: str
    text: Optional[str] = None


class HistoryOut(BaseModel):
    id: int
    question: str
    answer: str
    citations: list[HistoryCitation] = []
    created_at: str