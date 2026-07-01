from __future__ import annotations

from fastapi import FastAPI

from projects.optimalleads.leads.settings import get_settings
from telemetry import configure_telemetry
from projects.optimalleads.leads.infrastructure.persistence.bootstrap import get_leads_runtime
from projects.optimalleads.leads.presentation.api.router import router as leads_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_telemetry("optimalleads-leads")
    app = FastAPI(
        title="OptimalLeads Leads",
    )
    app.include_router(leads_router)

    app.state.leads_business_database_url = settings.business_database_url
    app.state.leads_outbox_database_url = settings.effective_outbox_database_url
    app.state.leads_audit_database_url = settings.effective_audit_database_url
    app.state.leads_events_database_url = settings.effective_events_database_url

    @app.on_event("startup")
    async def startup() -> None:
        await get_leads_runtime()

    return app
