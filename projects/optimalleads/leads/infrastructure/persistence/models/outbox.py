from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from projects.optimalleads.leads.infrastructure.persistence.models.base import Base
from projects.optimalleads.leads.infrastructure.persistence.constants import LEADS_OUTBOX_TABLE_NAME


class LeadsOutboxRow(Base):
	__tablename__ = LEADS_OUTBOX_TABLE_NAME

	event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
	aggregate_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
	event_name: Mapped[str] = mapped_column(String(255), nullable=False)
	event_kind: Mapped[str] = mapped_column(String(32), nullable=False)
	correlation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
	causation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
	occurred_at: Mapped[str | None] = mapped_column(String(64), nullable=True)
	payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.now(), nullable=False)


OutboxRow = LeadsOutboxRow