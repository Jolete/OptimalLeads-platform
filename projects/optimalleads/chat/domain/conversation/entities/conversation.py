from __future__ import annotations

from dataclasses import dataclass, field

from core_domain import AggregateRoot
from core_domain import ValidationError
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_id import ConversationId
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_title import ConversationTitle


@dataclass
class Conversation(AggregateRoot[ConversationId]):
    id: ConversationId
    title: ConversationTitle
    summary: str | None = None
    messages: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not isinstance(self.messages, list):
            raise ValidationError("Conversation messages must be a list")

    def append_message(self, message: str) -> None:
        self.messages.append(message)

    def update_title(self, title: str) -> None:
        self.title = ConversationTitle.create(title)

    def update_summary(self, summary: str | None) -> None:
        self.summary = summary.strip() if summary is not None else None

    def update_messages(self, messages: list[str]) -> None:
        self.messages = list(messages)
