from __future__ import annotations

import logging

from core_domain import Repository
from projects.optimalleads.chat.domain.conversation import Conversation, ConversationId


logger = logging.getLogger(__name__)


class ListConversationsUseCase:
    def __init__(self, repository: Repository[Conversation, ConversationId]) -> None:
        self._repository = repository

    async def execute(self) -> list[Conversation]:
        logger.info("chat.list.usecase.start", extra={"repository_type": type(self._repository).__name__})
        try:
            conversations = await self._repository.all()
            logger.info("chat.list.usecase.done", extra={"count": len(conversations)})
            return conversations
        except Exception:
            logger.exception("chat.list.usecase.failed", extra={"repository_type": type(self._repository).__name__})
            raise
