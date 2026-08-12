import asyncio
from datetime import datetime, timezone

from telethon.tl.types import Message, PeerChat

from src.config import Config
from src.fetcher import fetch_messages


def test_fetcher_stops_at_cursor_and_disconnects(monkeypatch):
    disconnected = False
    now = datetime.now(timezone.utc)
    source_messages = [
        Message(id=5, peer_id=PeerChat(1), date=now, message="five"),
        Message(id=4, peer_id=PeerChat(1), date=now, message="four"),
        Message(id=3, peer_id=PeerChat(1), date=now, message="three"),
    ]

    class FakeTelegramClient:
        async def get_entity(self, chat_id):
            return chat_id

        def iter_messages(self, entity, limit):
            async def generate():
                for message in source_messages:
                    yield message

            return generate()

    class FakeClient:
        def __init__(self, cfg):
            self.telegram = FakeTelegramClient()

        async def connect(self):
            return self.telegram

        async def disconnect(self):
            nonlocal disconnected
            disconnected = True

    monkeypatch.setattr("src.fetcher.Client", FakeClient)
    cfg = Config(groups=[1])

    result = asyncio.run(fetch_messages(cfg, hours_back=1, after_message_ids={1: 3}))

    assert [message["id"] for message in result[1]] == [4, 5]
    assert disconnected is True


def test_fetcher_skips_overflow_without_losing_cursor(monkeypatch):
    now = datetime.now(timezone.utc)
    source_messages = [
        Message(id=message_id, peer_id=PeerChat(1), date=now, message=str(message_id))
        for message_id in (5, 4, 3)
    ]

    class FakeTelegramClient:
        async def get_entity(self, chat_id):
            return chat_id

        def iter_messages(self, entity, limit):
            async def generate():
                for message in source_messages:
                    yield message

            return generate()

    class FakeClient:
        def __init__(self, cfg):
            self.telegram = FakeTelegramClient()

        async def connect(self):
            return self.telegram

        async def disconnect(self):
            return None

    monkeypatch.setattr("src.fetcher.Client", FakeClient)
    monkeypatch.setattr("src.fetcher.MAX_MESSAGES_PER_GROUP", 2)

    result = asyncio.run(fetch_messages(Config(groups=[1]), hours_back=1))

    assert result == {}
