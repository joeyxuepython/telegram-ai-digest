"""Configuration management — YAML file + env vars."""

from __future__ import annotations

import os
from datetime import datetime
from ipaddress import ip_address
from pathlib import Path

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramConfig(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    api_id: int = Field(default=0, alias="TELEGRAM_API_ID")
    api_hash: str = Field(default="", alias="TELEGRAM_API_HASH")
    session_path: str = "./data/session"

    @field_validator("api_id", mode="before")
    @classmethod
    def coerce_api_id(cls, v: object) -> int:
        return int(v) if v else 0


class AIConfig(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    provider: str = "openai"
    model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    base_url: str = ""
    max_tokens: int = 2000
    max_input_chars: int = 30000
    temperature: float = 0.3


class ScheduleConfig(BaseSettings):
    mode: str = "daily"  # hourly | daily | weekly
    time: str = "20:00"
    day: str = "monday"


class OutputConfig(BaseSettings):
    channels: list[str] = Field(default_factory=lambda: ["console"])
    webhook_url: str = ""
    language: str = "zh"


class ServerConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080
    allow_remote: bool = False


class Config(BaseSettings):
    model_config = {"populate_by_name": True}

    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    groups: list[int] = Field(default_factory=list)
    ai: AIConfig = Field(default_factory=AIConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    db_path: str = "./data/digests.db"

    def validate_for_digest(self) -> None:
        """Raise a clear error before connecting to Telegram or OpenAI."""
        missing: list[str] = []
        if not self.telegram.api_id:
            missing.append("TELEGRAM_API_ID")
        if not self.telegram.api_hash:
            missing.append("TELEGRAM_API_HASH")
        if not self.groups:
            missing.append("MONITOR_CHAT_IDS")
        if not self.ai.api_key:
            missing.append("OPENAI_API_KEY")
        if missing:
            raise ValueError("Missing required configuration: " + ", ".join(missing))
        if self.ai.provider != "openai":
            raise ValueError("Only the 'openai' provider is currently supported.")
        if self.ai.max_input_chars < 5000:
            raise ValueError("ai.max_input_chars must be at least 5000.")
        unknown_channels = set(self.output.channels) - {"console", "telegram", "webhook"}
        if unknown_channels:
            raise ValueError("Unknown output channels: " + ", ".join(sorted(unknown_channels)))
        if "webhook" in self.output.channels and not self.output.webhook_url:
            raise ValueError("output.webhook_url is required for webhook delivery.")

    def validate_schedule(self) -> None:
        """Validate schedule values before starting the long-running watcher."""
        if self.schedule.mode not in {"hourly", "daily", "weekly"}:
            raise ValueError("schedule.mode must be hourly, daily, or weekly.")
        try:
            datetime.strptime(self.schedule.time, "%H:%M")
        except ValueError as exc:
            raise ValueError("schedule.time must use 24-hour HH:MM format.") from exc
        if self.schedule.day.lower() not in {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        }:
            raise ValueError("schedule.day must be an English weekday name.")

    def validate_for_web(self) -> None:
        """Keep the unauthenticated history viewer local unless explicitly allowed."""
        try:
            is_loopback = ip_address(self.server.host).is_loopback
        except ValueError:
            is_loopback = self.server.host == "localhost"
        if not is_loopback and not self.server.allow_remote:
            raise ValueError(
                "Refusing to expose digest history remotely. "
                "Set server.allow_remote=true only behind trusted access controls."
            )

    @classmethod
    def from_yaml(cls, path: str | None = None) -> Config:
        """Load config from YAML file, then override with env vars."""
        cfg: dict = {}
        yaml_path = Path(path or "config.yaml")
        if yaml_path.exists():
            with open(yaml_path, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        telegram_cfg = dict(cfg.get("telegram", {}))
        ai_cfg = dict(cfg.get("ai", {}))
        schedule_cfg = dict(cfg.get("schedule", {}))
        output_cfg = dict(cfg.get("output", {}))
        if os.getenv("TELEGRAM_API_ID"):
            telegram_cfg["api_id"] = os.environ["TELEGRAM_API_ID"]
        if os.getenv("TELEGRAM_API_HASH"):
            telegram_cfg["api_hash"] = os.environ["TELEGRAM_API_HASH"]
        if os.getenv("OPENAI_API_KEY"):
            ai_cfg["api_key"] = os.environ["OPENAI_API_KEY"]
        if os.getenv("OPENAI_MODEL"):
            ai_cfg["model"] = os.environ["OPENAI_MODEL"]
        if os.getenv("TELEGRAM_SESSION_PATH"):
            telegram_cfg["session_path"] = os.environ["TELEGRAM_SESSION_PATH"]
        if os.getenv("DIGEST_MODE"):
            schedule_cfg["mode"] = os.environ["DIGEST_MODE"]
        if os.getenv("DIGEST_TIME"):
            schedule_cfg["time"] = os.environ["DIGEST_TIME"]
        if os.getenv("DIGEST_LANGUAGE"):
            output_cfg["language"] = os.environ["DIGEST_LANGUAGE"]

        return cls(
            telegram=TelegramConfig(**telegram_cfg),
            groups=[int(g) for g in os.environ.get("MONITOR_CHAT_IDS", "").split(",") if g.strip()]
            or cfg.get("groups", []),
            ai=AIConfig(**ai_cfg),
            schedule=ScheduleConfig(**schedule_cfg),
            output=OutputConfig(**output_cfg),
            server=ServerConfig(**cfg.get("server", {})),
            db_path=cfg.get("storage", {}).get("db_path", "./data/digests.db"),
        )


# Singleton
_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config.from_yaml()
    return _config


def set_config(config: Config) -> None:
    """Set the process-wide configuration used by optional web commands."""
    global _config
    _config = config
