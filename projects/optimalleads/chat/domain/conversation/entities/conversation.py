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
    messages: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not isinstance(self.messages, list):
            raise ValidationError("Conversation messages must be a list")

    def append_message(self, message: str) -> None:
        self.messages.append(message)
