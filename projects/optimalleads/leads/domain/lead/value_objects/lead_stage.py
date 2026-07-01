from __future__ import annotations

from dataclasses import dataclass

from core_domain import ValidationError, SimpleValueObject


@dataclass(frozen=True, slots=True)
class LeadStage(SimpleValueObject[str]):
    _ALLOWED_STAGES = {
        "new",
        "contacted",
        "qualified",
        "closed_won",
        "closed_lost",
    }

    def validate(self) -> None:
        val = self.value.strip().lower()
        if val not in self._ALLOWED_STAGES:
            raise ValidationError(
                f"Invalid lead stage: '{self.value}'. Allowed stages: {', '.join(sorted(self._ALLOWED_STAGES))}"
            )

    @classmethod
    def create(cls, value: str) -> "LeadStage":
        return cls(value=value.strip().lower())

    def __str__(self) -> str:
        return self.value
