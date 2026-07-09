from __future__ import annotations

from pydantic import BaseModel, Field


class IngestEventRequest(BaseModel):
    event_id: str = Field(min_length=1)
    aggregate_id: str = Field(min_length=1)
    event_name: str = Field(min_length=1)
    event_kind: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    causation_id: str | None = None
    occurred_at: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)