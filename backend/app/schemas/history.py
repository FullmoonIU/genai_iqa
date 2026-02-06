from pydantic import BaseModel


class HistoryOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: str
