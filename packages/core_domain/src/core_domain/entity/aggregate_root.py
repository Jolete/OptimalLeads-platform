from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

from core_domain.entity.entity import Entity
from core_domain.types import AggregateRootId


AggregateIdType = TypeVar("AggregateIdType", bound=AggregateRootId)


@dataclass(slots=True)
class AggregateRoot(Entity[AggregateIdType], Generic[AggregateIdType]):
    version: int = field(default=0, kw_only=True)
    domain_events: list[object] = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        Entity.__post_init__(self)
        if self.domain_events is None:
            self.domain_events = []

    def increment_version(self) -> None:
        self.version += 1

    def add_domain_event(self, event: object) -> None:
        self.domain_events.append(event)

    def clear_domain_events(self) -> None:
        self.domain_events.clear()