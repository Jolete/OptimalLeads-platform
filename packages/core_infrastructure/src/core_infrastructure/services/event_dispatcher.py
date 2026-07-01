from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from core_domain import EventEnvelope, EventKind
from core_domain.messaging import MessageBrokerPort


logger = logging.getLogger(__name__)
EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventDispatcher:
    def __init__(self, default_handler: EventHandler | None = None) -> None:
        self._handlers: dict[EventKind, EventHandler] = {}
        self._default_handler = default_handler

    def register_handler(self, event_kind: EventKind, handler: EventHandler) -> None:
        self._handlers[event_kind] = handler

    async def dispatch(self, event: EventEnvelope) -> bool:
        handler = self._handlers.get(event.event_kind, self._default_handler)
        if handler is None:
            logger.debug("No event handler registered for %s (%s)", event.event_name, event.event_kind)
            return False

        await handler(event)
        return True


def create_broker_dispatcher(broker: MessageBrokerPort) -> EventDispatcher:
    return EventDispatcher(default_handler=broker.publish)