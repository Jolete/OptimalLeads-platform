from __future__ import annotations

from core_domain import Repository
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationId


class GetConversationUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId]) -> None:
        self._repository = repository

    async def execute(self, conversation_id: str) -> Conversation | None:
        return await self._repository.get(conversation_id)
