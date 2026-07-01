from __future__ import annotations

from main import create_app
from logging_setup import configure_logging
from telemetry import configure_telemetry
from core_infrastructure import Settings

def get_settings() -> Settings:
    return Settings()


configure_logging()
configure_telemetry(get_settings().app_name)
app = create_app()
