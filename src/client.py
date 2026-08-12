"""Telegram client wrapper — connect, authenticate, fetch messages."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession

from .config import Config, get_config

logger = logging.getLogger(__name__)


class Client:
    """Thin wrapper around Telethon for message fetching."""

    def __init__(self, cfg: Optional[Config] = None) -> None:
        self.cfg = cfg or get_config()
        self._client: Optional[TelegramClient] = None

    async def connect(self) -> TelegramClient:
        if self._client and self._client.is_connected():
            return self._client

        session_dir = Path("data")
        session_dir.mkdir(exist_ok=True)

        self._client = TelegramClient(
            str(session_dir / "session"),
            self.cfg.telegram.api_id,
            self.cfg.telegram.api_hash,
        )
        await self._client.start()
        logger.info("Connected to Telegram as %s", await self._client.get_me())
        return self._client

    async def disconnect(self) -> None:
        if self._client:
            await self._client.disconnect()
            self._client = None
