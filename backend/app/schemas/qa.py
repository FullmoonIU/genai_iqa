from typing import Optional

from pydantic import BaseModel, Field


class AskIn(BaseModel):
    question: str
    top_k: int = Field(default=6, ge=1, le=20)


class Citation(BaseModel):
    source_name: str
    page: Optional[int] = None
    chunk_id: Optional[int] = None
    snippet: str
    text: Optional[str] = None


class AskOut(BaseModel):
    answer: str
    citations: list[Citation]