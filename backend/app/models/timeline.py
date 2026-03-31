"""SQLAlchemy models for the timeline feature."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, JSON, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimelineEntry(Base):
    """Timeline entry model for storing user timeline events."""

    __tablename__ = "timeline_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        index=True,
    )
    meta_data: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    __table_args__ = (
        Index("ix_timeline_user_timestamp", "user_id", "timestamp"),
    )
