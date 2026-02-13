from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class QAHistory(Base):
    __tablename__ = 'qa_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), index=True, nullable=False)

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    citations_json: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    feedback: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)