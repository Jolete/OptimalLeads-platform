from __future__ import annotations

import logging

import grpc
from google.protobuf.json_format import MessageToDict

from core_domain import EventEnvelope, EventKind
from projects.optimalleads.analytics.application.dto import IngestEventCommand
from projects.optimalleads.analytics.infrastructure.persistence.bootstrap import get_analytics_runtime

from . import analytics_internal_service_pb2, analytics_internal_service_pb2_grpc

logger = logging.getLogger(__name__)


class AnalyticsInternalService(analytics_internal_service_pb2_grpc.AnalyticsInternalServiceServicer):
    async def IngestEvent(self, request, context):
        runtime = await get_analytics_runtime()
        if runtime.mediator is None:
            await context.abort(grpc.StatusCode.UNAVAILABLE, "CQRS mediator is not available")

        event = EventEnvelope(
            event_id=request.event_id,
            aggregate_id=request.aggregate_id,
            event_name=request.event_name,
            event_kind=EventKind(request.event_kind),
            correlation_id=request.correlation_id,
            causation_id=request.causation_id or None,
            occurred_at=request.occurred_at or None,
            payload=MessageToDict(request.payload, preserving_proto_field_name=True),
        )
        await runtime.mediator.send(IngestEventCommand(event=event))
        return analytics_internal_service_pb2.IngestEventResponse(status="ingested")


async def create_grpc_server(host: str, port: int) -> grpc.aio.Server:
    server = grpc.aio.server()
    analytics_internal_service_pb2_grpc.add_AnalyticsInternalServiceServicer_to_server(AnalyticsInternalService(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    logger.info("analytics.grpc.started", extra={"host": host, "port": port})
    return server