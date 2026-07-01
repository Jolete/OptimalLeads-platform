"""MongoDB driver adapters."""

from core_infrastructure.drivers.mongodb.database_bootstrap import bootstrap_mongodb_database
from core_infrastructure.drivers.mongodb.database_composition import bootstrap_mongodb_database as _bootstrap_mongodb_database_registered
from core_infrastructure.drivers.mongodb.outbox_repository import MongoOutboxRepository
from core_infrastructure.drivers.mongodb.repository import MongoRepository

__all__ = ["MongoRepository", "MongoOutboxRepository", "bootstrap_mongodb_database", "_bootstrap_mongodb_database_registered"]
