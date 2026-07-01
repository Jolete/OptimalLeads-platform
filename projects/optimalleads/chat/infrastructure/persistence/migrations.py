from __future__ import annotations

from projects.optimalleads.chat.infrastructure.persistence.models.conversation import ConversationRow
from projects.optimalleads.chat.infrastructure.persistence.models.outbox import ChatOutboxRow


def get_chat_model_modules() -> tuple[type[ConversationRow], type[ChatOutboxRow]]:
    return (ConversationRow, ChatOutboxRow)
