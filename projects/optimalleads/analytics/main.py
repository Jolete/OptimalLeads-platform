from __future__ import annotations

from fastapi import FastAPI

from projects.optimalleads.analytics.settings import get_settings
from telemetry import configure_telemetry
from projects.optimalleads.analytics.infrastructure.persistence.bootstrap import get_analytics_runtime
from projects.optimalleads.analytics.presentation.api.router import router as analytics_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_telemetry("optimalleads-analytics")
    app = FastAPI(
        title="OptimalLeads Analytics",
    )
    app.include_router(analytics_router)

    app.state.analytics_business_database_url = settings.business_database_url
    app.state.analytics_outbox_database_url = settings.effective_outbox_database_url
    app.state.analytics_audit_database_url = settings.effective_audit_database_url
    app.state.analytics_events_database_url = settings.effective_events_database_url

    @app.on_event("startup")
    async def startup() -> None:
        await get_analytics_runtime()

    return app
