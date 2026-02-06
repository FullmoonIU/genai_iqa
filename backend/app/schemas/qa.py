from typing import Optional
from pydantic import BaseModel


class AskIn(BaseModel):
    question: str
    top_k: int = 6


class Citation(BaseModel):
    source_name: str
    page: Optional[int] = None
    chunk_id: Optional[int] = None
    snippet: str


class AskOut(BaseModel):
    answer: str
    citations: list[Citation]
