from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar


TResponse = TypeVar("TResponse")


class PipelineBehavior(Protocol[TResponse]):
    async def handle(self, request: Any, next_handler: Callable[[], Awaitable[TResponse]]) -> TResponse:
        ...