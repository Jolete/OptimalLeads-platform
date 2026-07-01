from __future__ import annotations

from dataclasses import dataclass

from core_domain import ValidationError, SimpleValueObject


@dataclass(frozen=True, slots=True)
class LeadName(SimpleValueObject[str]):
    def validate(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("Lead name cannot be empty")
        if len(self.value.strip()) > 100:
            raise ValidationError("Lead name cannot be longer than 100 characters")

    @classmethod
    def create(cls, value: str) -> "LeadName":
        return cls(value=value.strip())

    def __str__(self) -> str:
        return self.value
