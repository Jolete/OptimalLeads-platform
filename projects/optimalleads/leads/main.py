from __future__ import annotations

import logging

from fastapi import FastAPI

from projects.optimalleads.leads.settings import get_settings
from telemetry import configure_http_tracing, configure_telemetry
from projects.optimalleads.leads.infrastructure.persistence.bootstrap import get_leads_runtime
from projects.optimalleads.leads.infrastructure.persistence.constants import LEADS_SERVICE_NAME, LEADS_TITLE
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
        await get_leads_runtime()

    return app
