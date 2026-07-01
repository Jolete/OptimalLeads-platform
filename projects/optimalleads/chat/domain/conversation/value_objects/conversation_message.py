from __future__ import annotations

from dataclasses import dataclass

from core_domain import SimpleValueObject, ValidationError


@dataclass(frozen=True, slots=True)
class ConversationMessage(SimpleValueObject[str]):
    def validate(self) -> None:
        if not self.value or not self.value.strip():
            raise ValidationError("Conversation message cannot be empty")
        if len(self.value.strip()) > 500:
            raise ValidationError("Conversation message cannot be longer than 500 characters")

    @classmethod
    def create(cls, value: str) -> "ConversationMessage":
        return cls(value=value.strip())

    def __str__(self) -> str:
        return self.value