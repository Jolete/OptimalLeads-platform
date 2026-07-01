from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from projects.optimalleads.analytics.infrastructure.persistence.constants import ANALYTICS_PROJECTION_TABLE_NAME
from projects.optimalleads.analytics.infrastructure.persistence.models.base import Base


class ProjectionRow(Base):
    __tablename__ = ANALYTICS_PROJECTION_TABLE_NAME

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(200), nullable=False)
