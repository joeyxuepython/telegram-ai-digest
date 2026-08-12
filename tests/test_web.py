import asyncio
from datetime import datetime, timezone

from src.config import Config, set_config
from src.storage import Storage
from src.web import index


def test_web_escapes_digest_content(tmp_path):
    db_path = tmp_path / "digests.db"
    set_config(Config(db_path=str(db_path)))
    Storage(str(db_path)).save(
        [
            {
                "chat_id": 1,
                "title": "Test",
                "content": "<script>alert('xss')</script>",
                "message_count": 1,
                "participant_count": 1,
                "generated_at": datetime.now(timezone.utc),
            }
        ]
    )

    response = asyncio.run(index(chat_id=None))
    body = response.body.decode()

    assert "<script>" not in body
    assert "&lt;script&gt;" in body
