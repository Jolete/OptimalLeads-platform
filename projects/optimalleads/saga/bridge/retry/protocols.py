from __future__ import annotations

from typing import Protocol


class RetryPolicy(Protocol):
    def should_retry(self, attempt: int) -> bool: ...

    def next_delay_seconds(self, attempt: int) -> float: ...
