from datetime import datetime, timezone

import pytest

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


def test_storage_persists_digest_and_cursor_atomically(tmp_path):
    store = Storage(str(tmp_path / "digests.db"))
    digest = {
        "chat_id": 1,
        "title": "One",
        "content": "digest",
        "message_count": 2,
        "participant_count": 1,
        "generated_at": datetime.now(timezone.utc),
    }

    store.save_with_cursors([digest], {1: 42})

    assert store.get_last_message_ids([1]) == {1: 42}
    assert store.list(chat_id=1)[0]["content"] == "digest"


def test_storage_rolls_back_cursor_when_digest_save_fails(tmp_path):
    store = Storage(str(tmp_path / "digests.db"))
    store.save_with_cursors([], {1: 4})

    with pytest.raises(KeyError):
        store.save_with_cursors([{"chat_id": 1}], {1: 5})

    assert store.get_last_message_ids([1]) == {1: 4}
