"""Message fetcher — pull recent messages from monitored groups."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from telethon.tl.types import Message

from .client import Client
from .config import Config, get_config

logger = logging.getLogger(__name__)

# Max messages to fetch per group per digest run
MAX_MESSAGES_PER_GROUP = 500


async def fetch_messages(
    cfg: Config | None = None,
    hours_back: int = 24,
) -> dict[int, list[dict]]:
    """Fetch recent messages from all monitored groups.

    Returns: {chat_id: [{"id": 123, "text": "...", "sender": "...", "date": datetime}, ...]}
    """
    cfg = cfg or get_config()
    client = Client(cfg)
    tc = await client.connect()

    since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    result: dict[int, list[dict]] = {}

    for chat_id in cfg.groups:
        try:
            entity = await tc.get_entity(chat_id)
            messages: list[dict] = []
            async for msg in tc.iter_messages(
                entity, limit=MAX_MESSAGES_PER_GROUP, offset_date=since, reverse=True,
            ):
                if isinstance(msg, Message) and msg.message:
                    messages.append({
                        "id": msg.id,
                        "text": msg.message,
                        "sender": _sender_name(msg),
                        "date": msg.date,
                    })
            if messages:
                result[chat_id] = messages
                logger.info("Fetched %d messages from %s", len(messages), chat_id)
        except Exception as exc:
            logger.warning("Failed to fetch from %s: %s", chat_id, exc)

    await client.disconnect()
    return result


def _sender_name(msg: Message) -> str:
    """Extract a human-readable sender name."""
    sender = msg.sender
    if sender:
        first = getattr(sender, "first_name", None)
        last = getattr(sender, "last_name", None)
        username = getattr(sender, "username", None)
        if first:
            return f"{first} {last or ''}".strip()
        if username:
            return f"@{username}"
        return str(sender.id)
    return "Unknown"
