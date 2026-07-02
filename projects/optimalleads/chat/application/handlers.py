from __future__ import annotations

from projects.optimalleads.chat.application.dto import (
    AppendMessageCommand,
    CreateConversationCommand,
    DeleteConversationCommand,
    GetConversationQuery,
    ListConversationsQuery,
    UpdateConversationCommand,
)
from projects.optimalleads.chat.application.use_cases import (
    AppendMessageUseCase,
    CreateConversationUseCase,
    DeleteConversationUseCase,
    GetConversationUseCase,
    ListConversationsUseCase,
    UpdateConversationUseCase,
)


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


class UpdateConversationHandler:
    def __init__(self, use_case: UpdateConversationUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: UpdateConversationCommand):
        return await self._use_case.execute(
            request.conversation_id,
            request.title,
            request.summary,
            request.messages,
            request.correlation_id,
        )


class DeleteConversationHandler:
    def __init__(self, use_case: DeleteConversationUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: DeleteConversationCommand):
        return await self._use_case.execute(request.conversation_id, request.correlation_id)


class GetConversationHandler:
    def __init__(self, use_case: GetConversationUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: GetConversationQuery):
        return await self._use_case.execute(request.conversation_id)


class ListConversationsHandler:
    def __init__(self, use_case: ListConversationsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: ListConversationsQuery):
        return await self._use_case.execute()