"""Tests for the fetcher module."""

from src.fetcher import _sender_name


def test_sender_name_extraction():
    # Mock message object
    class MockSender:
        first_name = "John"
        last_name = "Doe"
        username = "johndoe"

    class MockMessage:
        sender = MockSender()
        id = 1

    assert _sender_name(MockMessage()) == "John Doe"
