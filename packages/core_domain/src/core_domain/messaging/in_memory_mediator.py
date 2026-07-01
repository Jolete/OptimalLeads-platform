from __future__ import annotations

from typing import Any

from core_domain.pipeline.pipeline_behavior import PipelineBehavior
from core_domain.messaging.handler import Handler
from core_domain.messaging.mediator import Mediator
from core_domain.messaging.request_handler_registry import RequestHandlerRegistry


class InMemoryMediator(Mediator):
    def __init__(self) -> None:
        self._handlers = RequestHandlerRegistry()
        self._behaviors: list[PipelineBehavior[Any]] = []

    def register_handler(self, request_type: type[Any], handler: Any) -> None:
        self._handlers.register(request_type, handler)

    def add_behavior(self, behavior: PipelineBehavior[Any]) -> None:
        self._behaviors.append(behavior)

    async def send(self, request: Any) -> Any:
        handler = self._handlers.resolve(request)

        async def _execute_chain(index: int) -> Any:
            if index < len(self._behaviors):
                behavior = self._behaviors[index]

                async def _next() -> Any:
                    return await _execute_chain(index + 1)

                return await behavior.handle(request, _next)

            if hasattr(handler, "handle"):
                return await handler.handle(request)
            if hasattr(handler, "execute"):
                return await handler.execute(request)
            raise TypeError(f"Handler {handler} must implement 'handle' or 'execute'")

        return await _execute_chain(0)