from __future__ import annotations

from core_domain import EventEnvelope, OutboxPort


class MongoOutboxRepository(OutboxPort):
    """MongoDB-specific outbox adapter placeholder.

    MongoDB can persist envelopes differently from SQLAlchemy-backed drivers,
    so this adapter lives next to the Mongo driver instead of reusing the
    generic SQLAlchemy implementation.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Mongo outbox persistence is driver-specific and not implemented yet")

    async def add(self, event: EventEnvelope) -> None:
        raise NotImplementedError

    async def drain(self) -> list[EventEnvelope]:
        raise NotImplementedError