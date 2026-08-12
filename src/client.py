"""Telegram client wrapper — connect, authenticate, fetch messages."""

from __future__ import annotations

import logging
from pathlib import Path

from telethon import TelegramClient

from .config import Config, get_config

logger = logging.getLogger(__name__)


class Client:
    """Thin wrapper around Telethon for message fetching."""

    def __init__(self, cfg: Config | None = None) -> None:
        self.cfg = cfg or get_config()
        self._client: TelegramClient | None = None

    async def connect(self) -> TelegramClient:
        if self._client and self._client.is_connected():
            return self._client

        session_path = Path(self.cfg.telegram.session_path)
        session_path.parent.mkdir(parents=True, exist_ok=True)

        self._client = TelegramClient(
            str(session_path),
            self.cfg.telegram.api_id,
            self.cfg.telegram.api_hash,
        )
        await self._client.start()
        session_file = (
            session_path
            if session_path.suffix == ".session"
            else session_path.with_suffix(".session")
        )
        try:
            session_file.chmod(0o600)
        except OSError as exc:
            logger.warning("Could not restrict Telegram session permissions: %s", exc)
        logger.info("Connected to Telegram")
        return self._client

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None
