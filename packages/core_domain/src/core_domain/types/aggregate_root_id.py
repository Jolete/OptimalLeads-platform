from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from core_domain.errors import ValidationError
from core_domain.value_object.value_object import ValueObject


TValue = TypeVar("TValue")


@dataclass(frozen=True, slots=True)
class AggregateRootId(ValueObject, Generic[TValue]):
    value: TValue

    @classmethod
    def create_unique(cls) -> "AggregateRootId[UUID]":
        return cls(uuid4())

    @classmethod
    def create(cls, value: TValue) -> "AggregateRootId[TValue]":
        if value is None:
            raise ValidationError("Aggregate root id cannot be null")
        return cls(value)

    def __str__(self) -> str:
        return str(self.value)


Guid = UUID
StringId = str
IntId = int
EntityId = AggregateRootId[Guid | StringId | IntId]