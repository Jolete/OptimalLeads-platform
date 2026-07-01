from __future__ import annotations

from typing import Any, Protocol


class Mediator(Protocol):
    async def send(self, request: Any) -> Any:
        ...