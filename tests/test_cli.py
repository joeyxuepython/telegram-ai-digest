import asyncio

from src.cli import _lookback_hours, _run_digest, _schedule_job
from src.config import Config, ScheduleConfig
from src.storage import Storage


def test_digest_cycle_advances_only_successful_chat_cursors(tmp_path, monkeypatch):
    db_path = tmp_path / "digests.db"
    cfg = Config(groups=[1, 2], db_path=str(db_path))
    captured_cursors: list[dict[int, int]] = []

    async def fake_fetch(cfg, hours_back, after_message_ids):
        captured_cursors.append(after_message_ids)
        return {
            1: [{"id": 10, "text": "one", "sender": "A", "date": "now"}],
            2: [{"id": 20, "text": "two", "sender": "B", "date": "now"}],
        }

    def fake_summarize(messages, cfg):
        return [
            {
                "chat_id": 1,
                "title": "One",
                "content": "digest",
                "message_count": 1,
                "participant_count": 1,
                "generated_at": "2025-01-01T00:00:00+00:00",
            }
        ]

    async def fake_deliver(digests, cfg):
        return None

    monkeypatch.setattr("src.cli.fetch_messages", fake_fetch)
    monkeypatch.setattr("src.cli.summarize", fake_summarize)
    monkeypatch.setattr("src.cli.deliver", fake_deliver)

    count = asyncio.run(_run_digest(cfg, 24))

    assert count == 1
    assert captured_cursors == [{}]
    assert Storage(str(db_path)).get_last_message_ids([1, 2]) == {1: 10}


def test_configured_weekly_schedule_and_lookback():
    cfg = Config(schedule=ScheduleConfig(mode="weekly", day="monday", time="08:30"))

    description = _schedule_job(lambda: None, cfg, interval=None)

    assert description == "weekly on monday at 08:30"
    assert _lookback_hours(cfg, interval=None) == 168
