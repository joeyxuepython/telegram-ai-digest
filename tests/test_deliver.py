import asyncio
from datetime import datetime, timezone

from src.config import Config, OutputConfig
from src.deliver import (
    TELEGRAM_MESSAGE_LIMIT,
    _deliver_webhook,
    _split_telegram_message,
    deliver,
)


def test_telegram_delivery_runs_inside_existing_event_loop(monkeypatch):
    sent: list[tuple[object, str]] = []
    disconnected = False

    class FakeTelegramClient:
        async def get_me(self):
            return "me"

        async def send_message(self, recipient, content):
            sent.append((recipient, content))

    class FakeClient:
        def __init__(self, cfg):
            self.telegram = FakeTelegramClient()

        async def connect(self):
            return self.telegram

        async def disconnect(self):
            nonlocal disconnected
            disconnected = True

    monkeypatch.setattr("src.client.Client", FakeClient)
    cfg = Config(output=OutputConfig(channels=["telegram"]))
    digests = [{"content": "Digest", "message_count": 1, "participant_count": 1}]

    asyncio.run(deliver(digests, cfg))

    assert sent == [("me", "Digest")]
    assert disconnected is True


def test_long_telegram_digest_is_split_within_limit():
    parts = _split_telegram_message("x" * (TELEGRAM_MESSAGE_LIMIT + 1))

    assert [len(part) for part in parts] == [TELEGRAM_MESSAGE_LIMIT, 1]


def test_webhook_serializes_digest_timestamp(monkeypatch):
    captured_payload: dict = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, url, json):
            captured_payload.update(json)
            return FakeResponse()

    monkeypatch.setattr("src.deliver.httpx.AsyncClient", FakeAsyncClient)
    cfg = Config(output=OutputConfig(webhook_url="https://example.com/hook"))
    generated_at = datetime.now(timezone.utc)

    asyncio.run(_deliver_webhook([{"generated_at": generated_at}], cfg))

    assert captured_payload["digests"][0]["generated_at"] == generated_at.isoformat()
