from __future__ import annotations

from abc import ABC, abstractmethod

from core_domain import EventEnvelope, OutboxPort


class ChatOutboxPort(OutboxPort, ABC):
    pass
