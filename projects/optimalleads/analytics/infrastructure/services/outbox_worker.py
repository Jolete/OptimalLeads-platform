from __future__ import annotations

from core_infrastructure.services import OutboxWorker
from core_infrastructure.services.event_dispatcher import EventDispatcher


class AnalyticsOutboxWorker(OutboxWorker):
    def __init__(self, outbox, dispatcher: EventDispatcher) -> None:
        super().__init__(outbox, dispatcher)