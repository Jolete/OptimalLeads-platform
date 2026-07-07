from __future__ import annotations

import logging

from fastapi import FastAPI

from projects.optimalleads.chat.settings import get_settings
from telemetry import configure_http_tracing, configure_telemetry
from projects.optimalleads.chat.infrastructure.persistence.bootstrap import get_chat_runtime
from projects.optimalleads.chat.infrastructure.persistence.constants import CHAT_SERVICE_NAME, CHAT_TITLE
from projects.optimalleads.chat.presentation.api.router import router as chat_router

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    settings = get_settings()
    configure_telemetry(CHAT_SERVICE_NAME)
    app = FastAPI(
        title=CHAT_TITLE,
    )
    configure_http_tracing(app, CHAT_SERVICE_NAME)
    app.include_router(chat_router)

    @app.on_event("startup")
    async def startup() -> None:
        app.state.business_database_url = settings.business_database_url
        await get_chat_runtime()

    return app
