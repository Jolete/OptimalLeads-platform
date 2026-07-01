from __future__ import annotations

from dataclasses import dataclass

from core_domain import ValidationError
from core_domain.contracts import EventEnvelope


@dataclass(frozen=True)
class IngestEventCommand:
    __command__ = True
    __query__ = False

    event: EventEnvelope

    def validate(self) -> None:
        if not self.event.event_name.strip():
            raise ValidationError("Event name cannot be empty")
        if not self.event.aggregate_id.strip():
            raise ValidationError("Aggregate id cannot be empty")
        if not self.event.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")
        if not isinstance(self.event.payload, dict):
            raise ValidationError("Event payload must be an object")


@dataclass(frozen=True)
class ReadSnapshotQuery:
    __command__ = False
    __query__ = True