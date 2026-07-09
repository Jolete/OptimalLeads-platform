from __future__ import annotations

import asyncio
import logging
from contextlib import suppress

from fastapi import FastAPI

from projects.optimalleads.leads.settings import get_settings
from telemetry import configure_http_tracing, configure_telemetry
from projects.optimalleads.leads.infrastructure.persistence.bootstrap import get_leads_runtime
from projects.optimalleads.leads.infrastructure.persistence.constants import LEADS_SERVICE_NAME, LEADS_TITLE
from projects.optimalleads.leads.presentation.grpc.server import create_grpc_server
from core_infrastructure.services import run_periodic_outbox_flush
from projects.optimalleads.leads.presentation.api.router import router as leads_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    settings = get_settings()
    configure_telemetry(LEADS_SERVICE_NAME)
    app = FastAPI(
        title=LEADS_TITLE,
    )
    configure_http_tracing(app, LEADS_SERVICE_NAME)
    app.include_router(leads_router)

    @app.on_event("startup")
    async def startup() -> None:
        runtime = await get_leads_runtime()
        if settings.internal_service_protocol == "grpc":
            app.state.grpc_server = await create_grpc_server(settings.grpc_listen_host, settings.grpc_listen_port)
        if runtime.outbox_worker is not None:
            app.state.outbox_task = asyncio.create_task(
                run_periodic_outbox_flush(runtime.outbox_worker, settings.outbox_flush_interval_seconds)
            )

    @app.on_event("shutdown")
    async def shutdown() -> None:
        outbox_task = getattr(app.state, "outbox_task", None)
        if outbox_task is not None:
            outbox_task.cancel()
            with suppress(asyncio.CancelledError):
                await outbox_task
        grpc_server = getattr(app.state, "grpc_server", None)
        if grpc_server is not None:
            await grpc_server.stop(0)

    return app
