"""CLI — the main entry point for Telegram AI Digest."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

import click
import schedule
import time as _time

from .config import Config, get_config
from .fetcher import fetch_messages
from .summarizer import summarize
from .deliver import deliver
from .storage import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tad")


@click.group()
@click.option("--config", "-c", default="config.yaml", help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, config: str) -> None:
    """Telegram AI Digest — AI-powered group chat summaries."""
    cfg = Config.from_yaml(config)
    # Store in module-level singleton
    import src.config as _cfg
    _cfg.config = cfg
    ctx.ensure_object(dict)
    ctx.obj["cfg"] = cfg


@cli.command()
@click.option("--hours", "-h", default=24, help="Hours of history to fetch")
@click.pass_context
def run(ctx: click.Context, hours: int) -> None:
    """Fetch messages and generate digests once."""
    cfg: Config = ctx.obj["cfg"]
    logger.info("Fetching messages from %d groups...", len(cfg.groups))

    async def _run():
        messages = await fetch_messages(cfg, hours_back=hours)
        if not messages:
            logger.warning("No messages fetched.")
            return
        digests = summarize(messages, cfg)
        if digests:
            store = Storage(cfg.db_path)
            store.save(digests)
            deliver(digests, cfg)
            logger.info("Done! %d digests generated.", len(digests))
        else:
            logger.warning("No digests generated.")

    asyncio.run(_run())


@cli.command()
@click.option("--interval", "-i", default=60, help="Check interval in minutes")
@click.pass_context
def watch(ctx: click.Context, interval: int) -> None:
    """Run continuously on a schedule."""
    cfg: Config = ctx.obj["cfg"]
    logger.info("Starting scheduler: every %d minutes", interval)

    def job():
        async def _run():
            messages = await fetch_messages(cfg, hours_back=interval)
            if messages:
                digests = summarize(messages, cfg)
                if digests:
                    store = Storage(cfg.db_path)
                    store.save(digests)
                    deliver(digests, cfg)
        asyncio.run(_run())

    schedule.every(interval).minutes.do(job)
    logger.info("First run now...")
    job()

    while True:
        schedule.run_pending()
        _time.sleep(30)


@cli.command()
@click.pass_context
def web(ctx: click.Context) -> None:
    """Start the web dashboard."""
    cfg: Config = ctx.obj["cfg"]
    from .web import main as web_main
    logger.info("Starting web dashboard at http://%s:%d", cfg.server.host, cfg.server.port)
    web_main()


@cli.command()
@click.option("--chat-id", "-c", type=int, default=None, help="Filter by chat ID")
@click.pass_context
def history(ctx: click.Context, chat_id: int | None) -> None:
    """Show past digests from the database."""
    cfg: Config = ctx.obj["cfg"]
    store = Storage(cfg.db_path)
    digests = store.list(chat_id=chat_id, limit=20)
    if not digests:
        click.echo("No digests found.")
        return
    for d in digests:
        click.echo("=" * 50)
        click.echo(d["content"])


def main():
    cli()


if __name__ == "__main__":
    main()
