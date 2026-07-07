from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from core_domain.pipeline.pipeline_behavior import PipelineBehavior


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class LoggingBehavior(PipelineBehavior[Any]):
    async def handle(self, request: Any, next_handler: Callable[[], Awaitable[Any]]) -> Any:
        request_name = type(request).__name__
        with tracer.start_as_current_span(f"cqrs.{request_name}") as span:
            logger.info("Handling %s...", request_name)
            start_time = time.perf_counter()
            try:
                response = await next_handler()
                elapsed = (time.perf_counter() - start_time) * 1000
                span.set_attribute("cqrs.request_name", request_name)
                span.set_attribute("cqrs.duration_ms", elapsed)
                logger.info("Handled %s successfully in %.2f ms.", request_name, elapsed)
                return response
            except Exception as error:
                elapsed = (time.perf_counter() - start_time) * 1000
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.set_attribute("cqrs.request_name", request_name)
                span.set_attribute("cqrs.duration_ms", elapsed)
                logger.exception("Failed handling %s after %.2f ms.", request_name, elapsed)
                raise