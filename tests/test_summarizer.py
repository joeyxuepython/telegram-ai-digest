"""Tests for the summarizer module."""

import pytest
from src.summarizer import build_prompt, summarize
from src.config import Config


def test_build_prompt_structure():
    messages = [
        {"id": 1, "text": "Hello world", "sender": "Alice", "date": "2025-01-01T10:00:00"},
        {"id": 2, "text": "Check this out: https://example.com", "sender": "Bob", "date": "2025-01-01T10:05:00"},
    ]
    prompt = build_prompt("Test Group", "en", messages)
    assert "Test Group" in prompt
    assert "Alice" in prompt
    assert "Bob" in prompt
    assert "https://example.com" in prompt


def test_summarize_empty_returns_empty():
    result = summarize({})
    assert result == []
