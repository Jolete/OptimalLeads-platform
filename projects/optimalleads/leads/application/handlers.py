from __future__ import annotations

from projects.optimalleads.leads.application.dto import (
    AdvanceLeadStageCommand,
    CreateLeadCommand,
    DeleteLeadCommand,
    GetLeadQuery,
    ListLeadsQuery,
    UpdateLeadCommand,
)
from projects.optimalleads.leads.application.use_cases import (
    AdvanceLeadStageUseCase,
    CreateLeadUseCase,
    DeleteLeadUseCase,
    GetLeadUseCase,
    ListLeadsUseCase,
    UpdateLeadUseCase,
)


class CreateLeadHandler:
    def __init__(self, use_case: CreateLeadUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: CreateLeadCommand):
        return await self._use_case.execute(request.name, request.correlation_id)


class UpdateLeadHandler:
    def __init__(self, use_case: UpdateLeadUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: UpdateLeadCommand):
        return await self._use_case.execute(request.lead_id, request.name, request.stage, request.notes, request.correlation_id)


class AdvanceLeadStageHandler:
    def __init__(self, use_case: AdvanceLeadStageUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: AdvanceLeadStageCommand):
        return await self._use_case.execute(request.lead_id, request.stage, request.correlation_id)


class DeleteLeadHandler:
    def __init__(self, use_case: DeleteLeadUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: DeleteLeadCommand):
        return await self._use_case.execute(request.lead_id, request.correlation_id)


class GetLeadHandler:
    def __init__(self, use_case: GetLeadUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: GetLeadQuery):
        return await self._use_case.execute(request.lead_id)


class ListLeadsHandler:
    def __init__(self, use_case: ListLeadsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: ListLeadsQuery):
        return await self._use_case.execute()