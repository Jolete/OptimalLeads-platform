from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValueObject:
    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        return None