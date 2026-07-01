from __future__ import annotations

from typing import Any, Protocol, TypeVar


TResponse = TypeVar("TResponse")


class Handler(Protocol[TResponse]):
    async def handle(self, request: Any) -> TResponse:
        ...