from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI

from fastapi_host.dependency_injection import add_application, add_infrastructure, add_presentation
from core_infrastructure import Container, Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_container() -> Container:
    container = Container(settings=get_settings())
    add_infrastructure(container)
    add_application(container)
    return container


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Host")
    add_presentation(app)
    return app
