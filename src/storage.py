"""SQLite storage for digest history."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    generated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_digests_chat ON digests(chat_id);
CREATE INDEX IF NOT EXISTS idx_digests_date ON digests(generated_at);
"""


class Storage:
    """Simple SQLite-backed digest store."""

    def __init__(self, db_path: str = "./data/digests.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.executescript(SCHEMA)

    def save(self, digests: list[dict]) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            for d in digests:
                conn.execute(
                    """INSERT INTO digests
                       (chat_id, title, content, message_count, participant_count, generated_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        d["chat_id"],
                        d["title"],
                        d["content"],
                        d.get("message_count", 0),
                        d.get("participant_count", 0),
                        d["generated_at"].isoformat() if isinstance(d["generated_at"], datetime) else d["generated_at"],
                    ),
                )
        logger.info("Saved %d digests to %s", len(digests), self.db_path)

    def list(self, chat_id: Optional[int] = None, limit: int = 20) -> list[dict]:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            if chat_id:
                rows = conn.execute(
                    "SELECT * FROM digests WHERE chat_id = ? ORDER BY generated_at DESC LIMIT ?",
                    (chat_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM digests ORDER BY generated_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]
