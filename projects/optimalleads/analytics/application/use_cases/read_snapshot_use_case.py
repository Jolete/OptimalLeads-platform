from __future__ import annotations

from projects.optimalleads.analytics.application.ports import AnalyticsStorePort
from projects.optimalleads.analytics.domain import Snapshot


class ReadSnapshotUseCase:
    def __init__(self, store: AnalyticsStorePort) -> None:
        self._store = store

    async def execute(self) -> Snapshot:
        return await self._store.get_snapshot()
