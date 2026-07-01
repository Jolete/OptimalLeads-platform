from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from core_domain.types import EntityId


IdType = TypeVar("IdType", bound=EntityId)


@dataclass(slots=True)
class Entity(Generic[IdType]):
    id: IdType

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        return None

    def same_identity(self, other: object) -> bool:
        return isinstance(other, Entity) and self.id == other.id