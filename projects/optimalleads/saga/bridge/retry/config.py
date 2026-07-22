from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class BaseRetrySettings:
    max_attempts: int
    backoff_seconds: float
    jitter_seconds: float
    timeout_seconds: float | None


@dataclass(slots=True)
class ChatRetrySettings(BaseRetrySettings):
    pass


@dataclass(slots=True)
class LeadsRetrySettings(BaseRetrySettings):
    pass
