from __future__ import annotations


class ChatApplicationError(Exception):
    pass


class ConversationNotFoundError(ChatApplicationError):
    def __init__(self, conversation_id: str) -> None:
        super().__init__(conversation_id)
        self.conversation_id = conversation_id
