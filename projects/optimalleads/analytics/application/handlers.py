from __future__ import annotations

from projects.optimalleads.analytics.application.dto import IngestEventCommand, ReadSnapshotQuery
from projects.optimalleads.analytics.application.use_cases import IngestEventsUseCase, ReadSnapshotUseCase


class IngestEventHandler:
    def __init__(self, use_case: IngestEventsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: IngestEventCommand):
        return await self._use_case.execute(request.event)


class ReadSnapshotHandler:
    def __init__(self, use_case: ReadSnapshotUseCase) -> None:
        self._use_case = use_case

    async def handle(self, request: ReadSnapshotQuery):
        return await self._use_case.execute()