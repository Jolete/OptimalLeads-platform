from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from typing import Any

from core_domain.pipeline.pipeline_behavior import PipelineBehavior
from core_domain.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)
_current_uow: ContextVar[UnitOfWork | None] = ContextVar("current_unit_of_work", default=None)


class TransactionBehavior(PipelineBehavior[Any]):
    def __init__(self, uow_provider: Callable[[], UnitOfWork]) -> None:
        self._uow_provider = uow_provider

    async def handle(self, request: Any, next_handler: Callable[[], Awaitable[Any]]) -> Any:
        if not getattr(request, "__command__", False):
            return await next_handler()

        request_name = type(request).__name__
        logger.info("Starting database transaction for command %s", request_name)
        uow = self._uow_provider()
        token = _current_uow.set(uow)

        async with uow:
            try:
                response = await next_handler()
                await uow.commit()
                logger.info("Committed database transaction for command %s", request_name)
                return response
            except Exception as ex:
                logger.error("Rolling back transaction for command %s due to: %s", request_name, ex)
                await uow.rollback()
                raise ex
            finally:
                _current_uow.reset(token)


def get_current_unit_of_work() -> UnitOfWork:
    uow = _current_uow.get()
    if uow is None:
        raise RuntimeError("No active unit of work")
    return uow