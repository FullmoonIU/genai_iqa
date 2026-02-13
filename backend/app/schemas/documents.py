from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    name: str
    type: str
    status: str
    created_at: str
