from __future__ import annotations

from typing import Any


class RequestHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[type[Any], Any] = {}

    def register(self, request_type: type[Any], handler: Any) -> None:
        self._handlers[request_type] = handler

    def resolve(self, request: Any) -> Any:
        request_type = type(request)
        handler = self._handlers.get(request_type)
        if handler is not None:
            return handler

        for registered_type, registered_handler in self._handlers.items():
            if issubclass(request_type, registered_type):
                return registered_handler

        raise KeyError(f"No handler registered for request type: {request_type.__name__}")