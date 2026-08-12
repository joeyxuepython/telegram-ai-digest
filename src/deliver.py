"""Delivery channels — send digests to various outputs."""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from .config import Config, get_config

logger = logging.getLogger(__name__)
TELEGRAM_MESSAGE_LIMIT = 4000


async def deliver(digests: list[dict], cfg: Config | None = None) -> None:
    """Deliver digests through configured channels."""
    cfg = cfg or get_config()
    if not digests:
        logger.info("No digests to deliver.")
        return

    for channel in cfg.output.channels:
        if channel == "console":
            _deliver_console(digests)
        elif channel == "telegram":
            await _deliver_telegram(digests, cfg)
        elif channel == "webhook":
            await _deliver_webhook(digests, cfg)
        else:
            logger.warning("Unknown output channel: %s", channel)


def _deliver_console(digests: list[dict]) -> None:
    for d in digests:
        print("=" * 60)
        print(d["content"])
        print(f"  ({d['message_count']} messages, {d['participant_count']} participants)")
    print("=" * 60)


async def _deliver_telegram(digests: list[dict], cfg: Config) -> None:
    from .client import Client

    client = Client(cfg)
    tc = await client.connect()
    try:
        me = await tc.get_me()
        for d in digests:
            try:
                for part in _split_telegram_message(str(d["content"])):
                    await tc.send_message(me, part)
                logger.info("Sent digest to Saved Messages")
            except Exception as exc:
                logger.error("Telegram delivery failed: %s", exc)
    finally:
        await client.disconnect()


async def _deliver_webhook(digests: list[dict], cfg: Config) -> None:
    if not cfg.output.webhook_url:
        logger.warning("Webhook URL not configured.")
        return
    try:
        payload = [
            {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in digest.items()
            }
            for digest in digests
        ]
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(cfg.output.webhook_url, json={"digests": payload})
        resp.raise_for_status()
        logger.info("Webhook delivered: %d digests", len(digests))
    except Exception as exc:
        logger.error("Webhook delivery failed: %s", exc)


def _split_telegram_message(content: str) -> list[str]:
    """Split long digests without exceeding Telegram's message limit."""
    if not content:
        return [""]
    return [
        content[start : start + TELEGRAM_MESSAGE_LIMIT]
        for start in range(0, len(content), TELEGRAM_MESSAGE_LIMIT)
    ]
