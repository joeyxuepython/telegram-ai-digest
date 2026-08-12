"""Delivery channels — send digests to various outputs."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import httpx

from .config import Config, get_config

logger = logging.getLogger(__name__)


def deliver(digests: list[dict], cfg: Optional[Config] = None) -> None:
    """Deliver digests through configured channels."""
    cfg = cfg or get_config()
    if not digests:
        logger.info("No digests to deliver.")
        return

    for channel in cfg.output.channels:
        if channel == "console":
            _deliver_console(digests)
        elif channel == "telegram":
            asyncio.run(_deliver_telegram(digests, cfg))
        elif channel == "webhook":
            _deliver_webhook(digests, cfg)
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
    me = await tc.get_me()
    for d in digests:
        try:
            await tc.send_message(me, d["content"])
            logger.info("Sent digest to Saved Messages")
        except Exception as exc:
            logger.error("Telegram delivery failed: %s", exc)
    await client.disconnect()


def _deliver_webhook(digests: list[dict], cfg: Config) -> None:
    if not cfg.output.webhook_url:
        logger.warning("Webhook URL not configured.")
        return
    try:
        resp = httpx.post(
            cfg.output.webhook_url,
            json={"digests": digests},
            timeout=30,
        )
        resp.raise_for_status()
        logger.info("Webhook delivered: %d digests", len(digests))
    except Exception as exc:
        logger.error("Webhook delivery failed: %s", exc)
