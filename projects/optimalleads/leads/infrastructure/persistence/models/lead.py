from __future__ import annotations

from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from projects.optimalleads.leads.infrastructure.persistence.constants import LEADS_TABLE_NAME
from projects.optimalleads.leads.infrastructure.persistence.models.base import Base


class LeadRow(Base):
    __tablename__ = LEADS_TABLE_NAME

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    stage: Mapped[str] = mapped_column(String(100), nullable=False, default="new")
    notes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
