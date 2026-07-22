from __future__ import annotations

from typing import Any

from .protocols import BrokerTransportPort


class KafkaBrokerProxy:
    def __init__(self, broker: Any) -> None:
        self._broker = broker

    async def start(self) -> None:
        await self._broker.start()

    async def close(self) -> None:
        await self._broker.close()

    def subscriber(self, *args: Any, **kwargs: Any):
        return self._broker.subscriber(*args, **kwargs)

    async def publish(self, *args: Any, **kwargs: Any):
        return await self._broker.publish(*args, **kwargs)


class RabbitBrokerProxy:
    def __init__(self, broker: Any) -> None:
        self._broker = broker

    async def start(self) -> None:
        await self._broker.start()

    async def close(self) -> None:
        await self._broker.close()

    def subscriber(self, *args: Any, **kwargs: Any):
        return self._broker.subscriber(*args, **kwargs)

    async def publish(self, *args: Any, **kwargs: Any):
        return await self._broker.publish(*args, **kwargs)
