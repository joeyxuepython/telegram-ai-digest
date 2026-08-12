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
    assert "[msg:1]" in prompt


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


def test_summarize_splits_large_inputs_without_dropping_messages(monkeypatch):
    calls: list[str] = []

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs["messages"][1]["content"])
            return type(
                "Response",
                (),
                {
                    "choices": [
                        type(
                            "Choice", (), {"message": type("Message", (), {"content": "Part"})()}
                        )()
                    ]
                },
            )()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr("src.summarizer.OpenAI", FakeOpenAI)
    cfg = Config(ai=AIConfig(api_key="test-key", max_input_chars=50))
    messages = {
        1: [
            {"id": 1, "text": "a" * 40, "sender": "Alice", "date": "2025-01-01"},
            {"id": 2, "text": "b" * 40, "sender": "Bob", "date": "2025-01-01"},
        ]
    }

    result = summarize(messages, cfg)

    assert len(calls) == 2
    assert "Part 1 of 2" in result[0]["content"]
    assert "Part 2 of 2" in result[0]["content"]
