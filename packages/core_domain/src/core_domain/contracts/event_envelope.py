from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    DOMAIN = "domain"               # Intern del propi servei
    INTEGRATION = "integration"     # Cap a altres serveis (Leads, Analytics)
    NOTIFICATION = "notification"   # Cap a la UI / WebSockets


class EventEnvelope(BaseModel):
    event_id: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1)
    event_name: str = Field(min_length=1)
    event_kind: EventKind = EventKind.INTEGRATION
    correlation_id: str = Field(min_length=1)
    causation_id: str | None = None
    occurred_at: str | None = None
    payload: dict[str, object]