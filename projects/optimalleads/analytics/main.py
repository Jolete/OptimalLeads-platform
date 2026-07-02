from __future__ import annotations

from fastapi import FastAPI

from projects.optimalleads.analytics.settings import get_settings
from telemetry import configure_telemetry
from projects.optimalleads.analytics.infrastructure.persistence.bootstrap import get_analytics_runtime
from projects.optimalleads.analytics.infrastructure.persistence.constants import ANALYTICS_SERVICE_NAME, ANALYTICS_TITLE
from projects.optimalleads.analytics.presentation.api.router import router as analytics_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_telemetry(ANALYTICS_SERVICE_NAME)
    app = FastAPI(
        title=ANALYTICS_TITLE,
    )
    app.include_router(analytics_router)

    @app.on_event("startup")
    async def startup() -> None:
        await get_analytics_runtime()

    return app
