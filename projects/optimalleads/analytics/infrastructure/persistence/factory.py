from __future__ import annotations

from collections.abc import Callable

from projects.optimalleads.analytics.infrastructure.persistence.memory import MemoryAnalyticsStore
from projects.optimalleads.analytics.infrastructure.persistence.store import AnalyticsSnapshotStore


def build_analytics_store_factory(session_factory: Callable[[], object]) -> Callable[[], AnalyticsSnapshotStore]:
    return lambda: AnalyticsSnapshotStore(session_factory())


def build_analytics_memory_store() -> MemoryAnalyticsStore:
    return MemoryAnalyticsStore()
