from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from core_domain import AggregateRootId, Guid


@dataclass(frozen=True, slots=True)
class SnapshotId(AggregateRootId[Guid]):
    @classmethod
    def create_unique(cls) -> "SnapshotId":
        return cls.create(uuid4())
