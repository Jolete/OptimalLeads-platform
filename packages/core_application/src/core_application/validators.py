from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


class Validator(Protocol[T]):
    def validate(self, value: T) -> None:
        ...
