from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


def create_analytics_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, future=True)


def create_analytics_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)
