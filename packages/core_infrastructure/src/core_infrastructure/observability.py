from __future__ import annotations

import logging

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


class TraceContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        span = trace.get_current_span()
        span_context = span.get_span_context() if span is not None else None
        if span_context is not None and span_context.is_valid:
            record.trace_id = f"{span_context.trace_id:032x}"
            record.span_id = f"{span_context.span_id:016x}"
        else:
            record.trace_id = "-"
            record.span_id = "-"
        return True


def configure_http_tracing(app: FastAPI, service_name: str | None = None) -> None:
    tracer = trace.get_tracer(service_name or app.title)

    @app.middleware("http")
    async def trace_http_requests(request: Request, call_next) -> Response:
        span_name = f"http {request.method} {request.url.path}"
        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.target", request.url.path)
            span.set_attribute("http.url", str(request.url))
            response = await call_next(request)
            span.set_attribute("http.status_code", response.status_code)
            return response


def configure_telemetry(service_name: str = "quantion-workspace") -> None:
    if trace.get_tracer_provider().__class__.__name__ != "ProxyTracerProvider":
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    logging.getLogger("opentelemetry").setLevel(logging.INFO)