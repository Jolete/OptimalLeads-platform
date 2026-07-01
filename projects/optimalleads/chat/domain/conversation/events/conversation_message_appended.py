from __future__ import annotations

from dataclasses import dataclass

from projects.optimalleads.chat.domain.conversation.value_objects.conversation_id import ConversationId
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_message import ConversationMessage


@dataclass(frozen=True)
class ConversationMessageAppended:
    conversation_id: ConversationId
    message: ConversationMessage
