from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol, TypeVar


TResponse = TypeVar("TResponse")


class ExecutionPipeline(Protocol):
    async def execute(self, request: object, handler: Callable[[], Awaitable[TResponse]]) -> TResponse:
        ...