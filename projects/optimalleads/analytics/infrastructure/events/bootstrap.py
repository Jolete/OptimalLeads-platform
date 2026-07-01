from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AnalyticsEventsRuntime:
    enabled: bool = True
