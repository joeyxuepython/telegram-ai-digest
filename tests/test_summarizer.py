"""Tests for the summarizer module."""

from src.config import AIConfig, Config
from src.summarizer import build_prompt, summarize


def test_build_prompt_structure():
    messages = [
        {"id": 1, "text": "Hello world", "sender": "Alice", "date": "2025-01-01T10:00:00"},
        {
            "id": 2,
            "text": "Check this out: https://example.com",
            "sender": "Bob",
            "date": "2025-01-01T10:05:00",
        },
    ]
    prompt = build_prompt("Test Group", "en", messages)
    assert "Test Group" in prompt
    assert "Alice" in prompt
    assert "Bob" in prompt
    assert "https://example.com" in prompt


def test_summarize_empty_returns_empty():
    result = summarize({})
    assert result == []


def test_summarize_uses_configured_client(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"] == "test-model"
            return type(
                "Response",
                (),
                {
                    "choices": [
                        type(
                            "Choice", (), {"message": type("Message", (), {"content": "Digest"})()}
                        )()
                    ]
                },
            )()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            assert kwargs["api_key"] == "test-key"
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("src.summarizer.OpenAI", FakeOpenAI)
    cfg = Config(ai=AIConfig(api_key="test-key", model="test-model"))
    messages = {1: [{"id": 1, "text": "Hello", "sender": "Alice", "date": "2025-01-01"}]}

    result = summarize(messages, cfg)

    assert result[0]["content"] == "Digest"
    assert result[0]["message_count"] == 1
