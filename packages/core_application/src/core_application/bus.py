from __future__ import annotations

from typing import Any, Awaitable, Callable, Protocol, TypeVar


class CommandBus:
    async def send(self, command: Any) -> Any:
        raise NotImplementedError


CommandT = TypeVar("CommandT")
ResponseT = TypeVar("ResponseT")


class CommandHandler(Protocol[CommandT, ResponseT]):
    async def handle(self, command: CommandT) -> ResponseT:
        ...


class Behavior(Protocol[CommandT, ResponseT]):
    async def handle(
        self,
        command: CommandT,
        next_handler: Callable[[CommandT], Awaitable[ResponseT]],
    ) -> ResponseT:
        ...
