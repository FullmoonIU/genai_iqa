from sqlalchemy import String, DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(32), nullable=False)

    status: Mapped[str] = mapped_column(String(32), default="uploaded", nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)

    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
