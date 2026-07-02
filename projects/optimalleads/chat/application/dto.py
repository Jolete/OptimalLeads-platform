from __future__ import annotations

from dataclasses import dataclass

from core_domain import ValidationError
from projects.optimalleads.chat.domain.conversation import ConversationId, ConversationMessage, ConversationTitle


@dataclass(frozen=True)
class CreateConversationCommand:
    __command__ = True
    __query__ = False

    title: str
    correlation_id: str | None = None

    def validate(self) -> None:
        ConversationTitle.create(self.title)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class AppendMessageCommand:
    __command__ = True
    __query__ = False

    conversation_id: str
    message: str
    correlation_id: str | None = None

    def validate(self) -> None:
        ConversationId.create(self.conversation_id)
        ConversationMessage.create(self.message)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class UpdateConversationCommand:
    __command__ = True
    __query__ = False

    conversation_id: str
    title: str
    summary: str | None = None
    messages: list[str] | None = None
    correlation_id: str | None = None

    def validate(self) -> None:
        ConversationId.create(self.conversation_id)
        ConversationTitle.create(self.title)
        if self.summary is not None and not self.summary.strip():
            raise ValidationError("Summary cannot be empty")
        if self.messages is not None:
            for message in self.messages:
                ConversationMessage.create(message)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class DeleteConversationCommand:
    __command__ = True
    __query__ = False

    conversation_id: str
    correlation_id: str | None = None

    def validate(self) -> None:
        ConversationId.create(self.conversation_id)
        if self.correlation_id is not None and not self.correlation_id.strip():
            raise ValidationError("Correlation id cannot be empty")


@dataclass(frozen=True)
class GetConversationQuery:
    __command__ = False
    __query__ = True

    conversation_id: str


@dataclass(frozen=True)
class ListConversationsQuery:
    __command__ = False
    __query__ = True
