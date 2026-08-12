"""Configuration management — YAML file + env vars."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class TelegramConfig(BaseSettings):
    api_id: int = Field(default=0, alias="TELEGRAM_API_ID")
    api_hash: str = Field(default="", alias="TELEGRAM_API_HASH")

    @field_validator("api_id", mode="before")
    @classmethod
    def coerce_api_id(cls, v: object) -> int:
        return int(v) if v else 0


class AIConfig(BaseSettings):
    provider: str = "openai"
    model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    api_key: str = Field(default="", alias="OPENAI_API_KEY")
    base_url: str = ""
    max_tokens: int = 2000
    temperature: float = 0.3


class ScheduleConfig(BaseSettings):
    mode: str = "daily"                     # hourly | daily | weekly
    time: str = "20:00"
    day: str = "monday"


class OutputConfig(BaseSettings):
    channels: list[str] = ["console"]
    webhook_url: str = ""
    language: str = "zh"


class ServerConfig(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080


class Config(BaseSettings):
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    groups: list[int] = Field(default_factory=list, alias="MONITOR_CHAT_IDS")
    ai: AIConfig = Field(default_factory=AIConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    db_path: str = "./data/digests.db"

    @classmethod
    def from_yaml(cls, path: Optional[str] = None) -> "Config":
        """Load config from YAML file, then override with env vars."""
        cfg: dict = {}
        yaml_path = Path(path or "config.yaml")
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        return cls(
            telegram=TelegramConfig(**cfg.get("telegram", {})),
            groups=[int(g) for g in
                    os.environ.get("MONITOR_CHAT_IDS", "").split(",") if g.strip()]
                    or cfg.get("groups", []),
            ai=AIConfig(**cfg.get("ai", {})),
            schedule=ScheduleConfig(**cfg.get("schedule", {})),
            output=OutputConfig(**cfg.get("output", {})),
            server=ServerConfig(**cfg.get("server", {})),
            db_path=cfg.get("storage", {}).get("db_path", "./data/digests.db"),
        )


# Singleton
config: Optional[Config] = None


def get_config() -> Config:
    global config
    if config is None:
        config = Config.from_yaml()
    return config
