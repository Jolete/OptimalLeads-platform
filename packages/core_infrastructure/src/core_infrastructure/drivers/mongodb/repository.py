from __future__ import annotations

from core_infrastructure.drivers.sqlalchemy.repository import SqlAlchemyRepository


class MongoRepository(SqlAlchemyRepository):
    """Provider-specific alias for MongoDB-backed repositories.

    The concrete Mongo adapter can replace this later without changing the
    application surface.
    """

    pass
