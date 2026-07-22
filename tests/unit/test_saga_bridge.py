from __future__ import annotations

import asyncio

from core_domain import EventEnvelope, EventKind
from projects.optimalleads.saga.bridge import (
    DeadLetterPublisher,
    FixedRetryPolicy,
    SagaBridge,
    SagaBridgeContract,
    SagaBridgeResponsibilities,
    SagaBridgeRoutePlan,
    SagaBridgeTopology,
)
from projects.optimalleads.saga.bridge.retry.config import ChatRetrySettings, LeadsRetrySettings


class FakeBroker:
    def __init__(self) -> None:
        self.started = 0
        self.closed = 0
        self.subscriptions: list[tuple[tuple[object, ...], dict[str, object], object]] = []

    async def start(self) -> None:
        self.started += 1

    async def close(self) -> None:
        self.closed += 1

    def subscriber(self, *args, **kwargs):
        def decorator(handler):
            self.subscriptions.append((args, kwargs, handler))
            return handler

        return decorator


class FakeDeadLetterPublisher:
    def __init__(self) -> None:
        self.calls: list[tuple[EventEnvelope, str]] = []

    async def publish(self, event: EventEnvelope, reason: str) -> None:
        self.calls.append((event, reason))


class RecordingHandler:
    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls: list[EventEnvelope] = []

    async def __call__(self, event: EventEnvelope) -> None:
        self.calls.append(event)
        if len(self.calls) <= self.failures:
            raise RuntimeError(f"boom-{len(self.calls)}")


class SleepRecorder:
    def __init__(self) -> None:
        self.calls: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.calls.append(delay)


def make_event() -> EventEnvelope:
    return EventEnvelope(
        event_id="event-1",
        aggregate_id="aggregate-1",
        event_name="ConversationCreated",
        event_kind=EventKind.DOMAIN,
        correlation_id="correlation-1",
        causation_id=None,
        occurred_at="2026-07-10T00:00:00+00:00",
        payload={"conversation_id": "conversation-1", "title": "ACME"},
    )


async def test_route_event_retries_and_sends_to_dead_letter() -> None:
    chat_broker = FakeBroker()
    leads_broker = FakeBroker()
    dead_letter_publisher = FakeDeadLetterPublisher()
    handler = RecordingHandler(failures=2)
    sleep_recorder = SleepRecorder()

    chat_retry_settings = ChatRetrySettings(
        max_attempts=3,
        backoff_seconds=0.5,
        jitter_seconds=0.0,
        timeout_seconds=None,
    )
    topology = SagaBridgeTopology(
        chat_broker_url="chat://broker",
        chat_broker_topic="chat.events",
        chat_consumer_group="chat-group",
        leads_broker_url="leads://broker",
        leads_broker_queue="leads.events",
        leads_consumer_group="leads-group",
        replay_topic="replay",
        chat_retry_topic="chat.retry",
        leads_retry_queue="leads.retry",
        chat_dead_letter_topic="chat.dlq",
        leads_dead_letter_queue="leads.dlq",
        max_retry_attempts=3,
        retry_backoff_seconds=0.5,
    )
    contract = SagaBridgeContract(
        inbound_chat=SagaBridgeRoutePlan("chat_inbound", True, "chat-group", "chat.retry", "chat.dlq", chat_retry_settings),
        inbound_leads=SagaBridgeRoutePlan("leads_inbound", True, "leads-group", "leads.retry", "leads.dlq", LeadsRetrySettings(max_attempts=5, backoff_seconds=2.0, jitter_seconds=0.0, timeout_seconds=None)),
    )

    bridge = SagaBridge(
        topology=topology,
        contract=contract,
        chat_broker=chat_broker,
        leads_broker=leads_broker,
        responsibilities=SagaBridgeResponsibilities(
            decode_event=lambda message: message,
            route_chat_event=handler,
            route_leads_event=handler,
            chat_retry_policy=FixedRetryPolicy(chat_retry_settings),
            chat_dead_letter_publisher=dead_letter_publisher,
        ),
    )

    original_sleep = asyncio.sleep
    asyncio.sleep = sleep_recorder  # type: ignore[assignment]
    try:
        await bridge._route_event(make_event(), handler, dead_letter_publisher)
    finally:
        asyncio.sleep = original_sleep  # type: ignore[assignment]

    assert len(handler.calls) == 3
    assert sleep_recorder.calls == [0.5, 1.0]
    assert dead_letter_publisher.calls == []


async def test_route_event_uses_dead_letter_when_retries_fail() -> None:
    dead_letter_publisher = FakeDeadLetterPublisher()
    handler = RecordingHandler(failures=10)
    chat_retry_settings = ChatRetrySettings(
        max_attempts=2,
        backoff_seconds=0.5,
        jitter_seconds=0.0,
        timeout_seconds=None,
    )
    topology = SagaBridgeTopology(
        chat_broker_url="chat://broker",
        chat_broker_topic="chat.events",
        chat_consumer_group="chat-group",
        leads_broker_url="leads://broker",
        leads_broker_queue="leads.events",
        leads_consumer_group="leads-group",
        replay_topic="replay",
        chat_retry_topic="chat.retry",
        leads_retry_queue="leads.retry",
        chat_dead_letter_topic="chat.dlq",
        leads_dead_letter_queue="leads.dlq",
        max_retry_attempts=2,
        retry_backoff_seconds=0.5,
    )
    contract = SagaBridgeContract(
        inbound_chat=SagaBridgeRoutePlan("chat_inbound", True, "chat-group", "chat.retry", "chat.dlq", chat_retry_settings),
        inbound_leads=SagaBridgeRoutePlan("leads_inbound", True, "leads-group", "leads.retry", "leads.dlq", LeadsRetrySettings(max_attempts=5, backoff_seconds=2.0, jitter_seconds=0.0, timeout_seconds=None)),
    )

    bridge = SagaBridge(
        topology=topology,
        contract=contract,
        chat_broker=FakeBroker(),
        leads_broker=FakeBroker(),
        responsibilities=SagaBridgeResponsibilities(
            decode_event=lambda message: message,
            route_chat_event=handler,
            route_leads_event=handler,
            chat_retry_policy=FixedRetryPolicy(chat_retry_settings),
            chat_dead_letter_publisher=dead_letter_publisher,
        ),
    )

    try:
        await bridge._route_event(make_event(), handler, dead_letter_publisher)
    except RuntimeError as error:
        assert str(error) == "boom-2"
    else:
        raise AssertionError("Expected RuntimeError")

    assert len(dead_letter_publisher.calls) == 1
    assert dead_letter_publisher.calls[0][1] == "boom-2"
