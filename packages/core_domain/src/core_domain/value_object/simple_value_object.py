from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from core_domain.value_object.value_object import ValueObject


ValueType = TypeVar("ValueType")


@dataclass(frozen=True, slots=True)
class SimpleValueObject(ValueObject, Generic[ValueType]):
    value: ValueType