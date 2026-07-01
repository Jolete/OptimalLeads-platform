from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Validatable(Protocol):
    def validate(self) -> None:
        ...


@runtime_checkable
class Validator(Protocol):
    def validate(self, request: Any) -> None:
        ...


ValidationRule = Callable[[Any], None]