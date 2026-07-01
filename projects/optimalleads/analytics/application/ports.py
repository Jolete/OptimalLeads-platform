from __future__ import annotations

from abc import ABC, abstractmethod

from core_domain import EventEnvelope, OutboxPort
from projects.optimalleads.analytics.domain import Snapshot


class AnalyticsStorePort(ABC):
    @abstractmethod
    async def upsert_snapshot(self, snapshot: Snapshot) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_snapshot(self) -> Snapshot:
        raise NotImplementedError


class AnalyticsOutboxPort(OutboxPort, ABC):
    pass
