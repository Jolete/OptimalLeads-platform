from __future__ import annotations

from projects.optimalleads.analytics.application.ports import AnalyticsStorePort
from projects.optimalleads.analytics.domain import Snapshot


class MemoryAnalyticsStore(AnalyticsStorePort):
    def __init__(self) -> None:
        self._snapshot = Snapshot()

    async def get_snapshot(self) -> Snapshot:
        return self._snapshot

    async def upsert_snapshot(self, snapshot: Snapshot) -> None:
        self._snapshot = snapshot
