from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from core_domain.pipeline.pipeline_behavior import PipelineBehavior


logger = logging.getLogger(__name__)


class LoggingBehavior(PipelineBehavior[Any]):
    async def handle(self, request: Any, next_handler: Callable[[], Awaitable[Any]]) -> Any:
        request_name = type(request).__name__
        logger.info("Handling %s...", request_name)
        start_time = time.perf_counter()
        try:
            response = await next_handler()
            return response
        finally:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info("Handled %s successfully in %.2f ms.", request_name, elapsed)