from __future__ import annotations

import asyncio

from logging_setup import configure_logging
from telemetry import configure_telemetry
from projects.optimalleads.saga.constants import SAGA_SERVICE_NAME
from projects.optimalleads.saga.consumer import build_saga_consumer


async def run() -> None:
    configure_logging()
    configure_telemetry(SAGA_SERVICE_NAME)
    consumer = await build_saga_consumer()
    await consumer.run_forever()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()