from __future__ import annotations

from typing import Any

from core_domain.messaging.in_memory_mediator import InMemoryMediator
from core_domain.unit_of_work import UnitOfWork
from core_domain.pipeline.logging_behavior import LoggingBehavior
from core_domain.pipeline.transaction_behavior import TransactionBehavior
from core_domain.pipeline.validation_behavior import ValidationBehavior


class CqrsMediator(InMemoryMediator):
    def __init__(self, uow_provider: callable[[], UnitOfWork] | None = None) -> None:
        super().__init__()
        self.add_behavior(LoggingBehavior())
        self.add_behavior(ValidationBehavior())
        if uow_provider is not None:
            self.add_behavior(TransactionBehavior(uow_provider))

    def register_handler(self, request_type: type[Any], handler: Any) -> None:
        super().register_handler(request_type, handler)
