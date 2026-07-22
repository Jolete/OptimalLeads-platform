from __future__ import annotations

from .config import BaseRetrySettings
from .protocols import RetryPolicy


class FixedRetryPolicy:
    def __init__(self, settings: BaseRetrySettings) -> None:
        self._settings = settings

    def should_retry(self, attempt: int) -> bool:
        return attempt < self._settings.max_attempts

    def next_delay_seconds(self, attempt: int) -> float:
        return float(self._settings.backoff_seconds * attempt)
