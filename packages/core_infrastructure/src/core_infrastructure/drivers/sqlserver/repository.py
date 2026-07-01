from __future__ import annotations

from core_infrastructure.drivers.sqlalchemy.repository import SqlAlchemyRepository


class SqlServerRepository(SqlAlchemyRepository):
    """Provider-specific alias for SQL Server-backed SQLAlchemy repositories."""

    pass
