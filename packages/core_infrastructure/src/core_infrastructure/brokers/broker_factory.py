from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from core_domain.broker_config import BrokerConfig
from core_domain.messaging import MessageBrokerPort


class BrokerFactory(ABC):
    @abstractmethod
    def create(self, settings: BrokerConfig) -> MessageBrokerPort:
        raise NotImplementedError


BrokerFactoryProvider = Callable[[BrokerConfig], MessageBrokerPort]


_BROKER_FACTORIES: dict[str, BrokerFactoryProvider] = {}


def register_broker(provider: str, factory: BrokerFactoryProvider) -> None:
    _BROKER_FACTORIES[provider] = factory


def create_broker(settings: BrokerConfig) -> MessageBrokerPort:
    provider = settings.broker_provider
    try:
        factory = _BROKER_FACTORIES[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported broker provider: {provider}") from exc

    return factory(settings)