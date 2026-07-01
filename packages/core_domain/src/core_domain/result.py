from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class Result(Generic[T]):
    value: T | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return not self.errors

    @property
    def is_failure(self) -> bool:
        return bool(self.errors)

    @classmethod
    def ok(cls, value: T | None = None) -> "Result[T]":
        return cls(value=value)

    @classmethod
    def fail(cls, *errors: str) -> "Result[T]":
        return cls(errors=list(errors))
