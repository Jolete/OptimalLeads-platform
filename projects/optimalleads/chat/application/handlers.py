from __future__ import annotations

from projects.optimalleads.chat.application.dto import AppendMessageCommand, CreateConversationCommand, DeleteConversationCommand
from projects.optimalleads.chat.application.use_cases import AppendMessageUseCase, CreateConversationUseCase, DeleteConversationUseCase


class CreateConversationHandler:
    def __init__(self, use_case: CreateConversationUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: CreateConversationCommand):
        return await self._use_case.execute(request)


class AppendMessageHandler:
    def __init__(self, use_case: AppendMessageUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: AppendMessageCommand):
        return await self._use_case.execute(request)


class DeleteConversationHandler:
    def __init__(self, use_case: DeleteConversationUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: DeleteConversationCommand):
        return await self._use_case.execute(request.conversation_id, request.correlation_id)