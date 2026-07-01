from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from projects.optimalleads.chat.infrastructure.persistence.constants import CHAT_CONVERSATIONS_TABLE_NAME
from projects.optimalleads.chat.infrastructure.persistence.models.base import Base


class ConversationRow(Base):
    __tablename__ = CHAT_CONVERSATIONS_TABLE_NAME

    conversation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    messages: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
