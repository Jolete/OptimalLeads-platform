from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from core_domain import EventEnvelope, EventKind
from core_domain.messaging import MessageBrokerPort
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)
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

        with tracer.start_as_current_span(f"event.dispatch.{event.event_name}") as span:
            span.set_attribute("event.name", event.event_name)
            span.set_attribute("event.kind", event.event_kind.value)
            span.set_attribute("event.aggregate_id", event.aggregate_id)
            span.set_attribute("event.correlation_id", event.correlation_id)
            try:
                await handler(event)
                return True
            except Exception as error:
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise


def create_broker_dispatcher(broker: MessageBrokerPort) -> EventDispatcher:
    return EventDispatcher(default_handler=broker.publish)