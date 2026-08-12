import pytest

from src.config import AIConfig, Config, ServerConfig, TelegramConfig


def test_digest_validation_reports_missing_values():
    with pytest.raises(ValueError, match="TELEGRAM_API_ID"):
        Config().validate_for_digest()


def test_environment_overrides_yaml(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """telegram:\n  api_id: 1\n  api_hash: yaml-hash\ngroups: [10]\nai:\n  api_key: yaml-key\n""",
        encoding="utf-8",
    )
    monkeypatch.setenv("TELEGRAM_API_ID", "2")
    monkeypatch.setenv("TELEGRAM_API_HASH", "env-hash")
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("MONITOR_CHAT_IDS", "20,30")

    cfg = Config.from_yaml(str(config_file))

    assert cfg.telegram.api_id == 2
    assert cfg.telegram.api_hash == "env-hash"
    assert cfg.ai.api_key == "env-key"
    assert cfg.groups == [20, 30]


def test_digest_validation_accepts_complete_openai_config():
    cfg = Config(
        telegram=TelegramConfig(api_id=1, api_hash="hash"),
        groups=[1],
        ai=AIConfig(api_key="key"),
    )

    cfg.validate_for_digest()


def test_schedule_and_language_environment_overrides(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("schedule:\n  mode: daily\noutput:\n  language: en\n", encoding="utf-8")
    monkeypatch.setenv("DIGEST_MODE", "weekly")
    monkeypatch.setenv("DIGEST_TIME", "08:30")
    monkeypatch.setenv("DIGEST_LANGUAGE", "zh")

    cfg = Config.from_yaml(str(config_file))

    assert cfg.schedule.mode == "weekly"
    assert cfg.schedule.time == "08:30"
    assert cfg.output.language == "zh"


def test_schedule_validation_rejects_invalid_time():
    cfg = Config()
    cfg.schedule.time = "25:00"

    with pytest.raises(ValueError, match="HH:MM"):
        cfg.validate_schedule()


def test_web_requires_explicit_remote_opt_in():
    cfg = Config(server=ServerConfig(host="0.0.0.0"))

    with pytest.raises(ValueError, match="Refusing to expose"):
        cfg.validate_for_web()


def test_digest_validation_rejects_unbounded_small_prompt_limit():
    cfg = Config(
        telegram=TelegramConfig(api_id=1, api_hash="hash"),
        groups=[1],
        ai=AIConfig(api_key="key", max_input_chars=1000),
    )

    with pytest.raises(ValueError, match="at least 5000"):
        cfg.validate_for_digest()
