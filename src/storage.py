"""SQLite storage for digest history."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

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
CREATE TABLE IF NOT EXISTS chat_state (
    chat_id INTEGER PRIMARY KEY,
    last_message_id INTEGER NOT NULL
);
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
            self._save_digests(conn, digests)
        logger.info("Saved %d digests to %s", len(digests), self.db_path)

    def save_with_cursors(self, digests: list[dict], cursors: dict[int, int]) -> None:
        """Atomically persist generated digests and their processed message cursors."""
        with sqlite3.connect(str(self.db_path)) as conn:
            self._save_digests(conn, digests)
            for chat_id, last_message_id in cursors.items():
                conn.execute(
                    """INSERT INTO chat_state (chat_id, last_message_id) VALUES (?, ?)
                       ON CONFLICT(chat_id) DO UPDATE SET last_message_id = excluded.last_message_id""",
                    (chat_id, last_message_id),
                )
        logger.info("Saved %d digests and %d chat cursors", len(digests), len(cursors))

    @staticmethod
    def _save_digests(conn: sqlite3.Connection, digests: list[dict]) -> None:
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
                    d["generated_at"].isoformat()
                    if isinstance(d["generated_at"], datetime)
                    else d["generated_at"],
                ),
            )

    def get_last_message_ids(self, chat_ids: list[int]) -> dict[int, int]:
        if not chat_ids:
            return {}
        placeholders = ",".join("?" for _ in chat_ids)
        with sqlite3.connect(str(self.db_path)) as conn:
            rows = conn.execute(
                f"SELECT chat_id, last_message_id FROM chat_state WHERE chat_id IN ({placeholders})",
                chat_ids,
            ).fetchall()
        return {int(chat_id): int(message_id) for chat_id, message_id in rows}

    def list(self, chat_id: int | None = None, limit: int = 20) -> list[dict]:
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            if chat_id is not None:
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
