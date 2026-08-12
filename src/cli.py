"""CLI — the main entry point for Telegram AI Digest."""

from __future__ import annotations

import asyncio
import logging
import time as _time

import click
import schedule

from .config import Config, set_config
from .deliver import deliver
from .fetcher import fetch_messages
from .storage import Storage
from .summarizer import summarize

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("tad")


async def _run_digest(cfg: Config, hours: int) -> int:
    """Run one incremental digest cycle and return the number generated."""
    store = Storage(cfg.db_path)
    last_message_ids = store.get_last_message_ids(cfg.groups)
    messages = await fetch_messages(
        cfg,
        hours_back=hours,
        after_message_ids=last_message_ids,
    )
    if not messages:
        logger.warning("No new messages fetched.")
        return 0

    digests = summarize(messages, cfg)
    if not digests:
        logger.warning("No digests generated; message cursors were not advanced.")
        return 0

    successful_chat_ids = {int(digest["chat_id"]) for digest in digests}
    cursors = {
        chat_id: max(int(message["id"]) for message in chat_messages)
        for chat_id, chat_messages in messages.items()
        if chat_id in successful_chat_ids
    }
    store.save_with_cursors(digests, cursors)
    await deliver(digests, cfg)
    logger.info("Done! %d digests generated.", len(digests))
    return len(digests)


def _schedule_job(job, cfg: Config, interval: int | None) -> str:
    """Register one watcher job and return a human-readable schedule."""
    schedule.clear()
    if interval is not None:
        schedule.every(interval).minutes.do(job)
        return f"every {interval} minutes"
    if cfg.schedule.mode == "hourly":
        schedule.every().hour.at(":00").do(job)
        return "hourly"
    if cfg.schedule.mode == "daily":
        schedule.every().day.at(cfg.schedule.time).do(job)
        return f"daily at {cfg.schedule.time}"
    weekday = getattr(schedule.every(), cfg.schedule.day.lower())
    weekday.at(cfg.schedule.time).do(job)
    return f"weekly on {cfg.schedule.day.lower()} at {cfg.schedule.time}"


def _lookback_hours(cfg: Config, interval: int | None) -> int:
    if interval is not None:
        return max(1, (interval + 59) // 60)
    return {"hourly": 1, "daily": 24, "weekly": 24 * 7}[cfg.schedule.mode]


@click.group()
@click.option("--config", "-c", default="config.yaml", help="Path to config file")
@click.pass_context
def cli(ctx: click.Context, config: str) -> None:
    """Telegram AI Digest — AI-powered group chat summaries."""
    cfg = Config.from_yaml(config)
    set_config(cfg)
    ctx.ensure_object(dict)
    ctx.obj["cfg"] = cfg


@cli.command()
@click.option(
    "--hours", "-h", default=24, type=click.IntRange(min=1), help="Hours of history to fetch"
)
@click.pass_context
def run(ctx: click.Context, hours: int) -> None:
    """Fetch messages and generate digests once."""
    cfg: Config = ctx.obj["cfg"]
    try:
        cfg.validate_for_digest()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    logger.info("Fetching messages from %d groups...", len(cfg.groups))

    asyncio.run(_run_digest(cfg, hours))


@cli.command()
@click.option(
    "--interval",
    "-i",
    default=None,
    type=click.IntRange(min=1),
    help="Override config schedule with a fixed interval in minutes",
)
@click.pass_context
def watch(ctx: click.Context, interval: int | None) -> None:
    """Run continuously on a schedule."""
    cfg: Config = ctx.obj["cfg"]
    try:
        cfg.validate_for_digest()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
    if interval is None:
        try:
            cfg.validate_schedule()
        except ValueError as exc:
            raise click.UsageError(str(exc)) from exc

    def job():
        asyncio.run(_run_digest(cfg, _lookback_hours(cfg, interval)))

    description = _schedule_job(job, cfg, interval)
    logger.info("Starting scheduler: %s", description)
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
    try:
        cfg.validate_for_web()
    except ValueError as exc:
        raise click.UsageError(str(exc)) from exc
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
