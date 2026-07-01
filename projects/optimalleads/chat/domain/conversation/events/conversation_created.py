from __future__ import annotations

from dataclasses import dataclass

from projects.optimalleads.chat.domain.conversation.value_objects.conversation_id import ConversationId
from projects.optimalleads.chat.domain.conversation.value_objects.conversation_title import ConversationTitle


@dataclass(frozen=True)
class ConversationCreated:
    conversation_id: ConversationId
    title: ConversationTitle
