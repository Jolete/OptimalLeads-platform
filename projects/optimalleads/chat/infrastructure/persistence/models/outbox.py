from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from projects.optimalleads.chat.infrastructure.persistence.constants import CHAT_OUTBOX_TABLE_NAME
from projects.optimalleads.chat.infrastructure.persistence.models.base import Base


class ChatOutboxRow(Base):
	__tablename__ = CHAT_OUTBOX_TABLE_NAME

	event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
	aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
	event_name: Mapped[str] = mapped_column(String(255), nullable=False)
	event_kind: Mapped[str] = mapped_column(String(32), nullable=False)
	correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
	causation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
	occurred_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
	payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)
