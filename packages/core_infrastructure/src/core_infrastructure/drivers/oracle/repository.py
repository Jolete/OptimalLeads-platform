from __future__ import annotations

from core_infrastructure.drivers.sqlalchemy.repository import SqlAlchemyRepository


class OracleRepository(SqlAlchemyRepository):
    """Provider-specific alias for Oracle-backed SQLAlchemy repositories."""

    pass
