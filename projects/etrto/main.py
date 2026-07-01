from __future__ import annotations

from fastapi import FastAPI

from projects.etrto.presentation.api.router import router as etrto_router


def create_app() -> FastAPI:
    app = FastAPI(title="ETRTO API")
    app.include_router(etrto_router)
    return app
