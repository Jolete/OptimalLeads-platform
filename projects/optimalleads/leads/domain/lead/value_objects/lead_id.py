from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from core_domain import AggregateRootId, Guid


@dataclass(frozen=True, slots=True)
class LeadId(AggregateRootId[Guid]):
    @classmethod
    def create_unique(cls) -> "LeadId":
        return cls.create(uuid4())

    def __str__(self) -> str:
        return str(self.value)
