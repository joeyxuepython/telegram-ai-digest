from datetime import datetime, timezone

from src.storage import Storage


def test_storage_filters_by_zero_chat_id(tmp_path):
    store = Storage(str(tmp_path / "digests.db"))
    store.save(
        [
            {
                "chat_id": 0,
                "title": "Zero",
                "content": "one",
                "message_count": 1,
                "participant_count": 1,
                "generated_at": datetime.now(timezone.utc),
            },
            {
                "chat_id": 1,
                "title": "One",
                "content": "two",
                "message_count": 1,
                "participant_count": 1,
                "generated_at": datetime.now(timezone.utc),
            },
        ]
    )

    assert [digest["chat_id"] for digest in store.list(chat_id=0)] == [0]
