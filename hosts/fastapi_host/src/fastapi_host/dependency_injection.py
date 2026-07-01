from __future__ import annotations

from fastapi import FastAPI

from fastapi_host.routers.chat import router as chat_router
from projects.chat.infrastructure.composition.container import Container


def add_presentation(app: FastAPI) -> FastAPI:
    """Equivalent a AddPresentation() de .NET."""
    app.include_router(chat_router)
    return app


def add_infrastructure(container: Container) -> Container:
    """Equivalent a AddInfrastructure()/AddPersistence() de .NET."""
    # Pre-warm bàsic dels adapters externs per validar configuració en startup.
    container.memory()
    container.llm()
    return container


def add_application(container: Container) -> Container:
    """Equivalent a AddApplication() de .NET."""
    container.command_bus()
    return container
