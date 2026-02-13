from typing import Optional

from sqlalchemy import Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id"), index=True, nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    document = relationship("Document", back_populates="chunks")
