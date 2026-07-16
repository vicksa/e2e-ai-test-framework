import os

import pytest

from e2e_ai.llm_backend import is_available, normalize


def test_is_available_false_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert is_available() is False


def test_is_available_true_with_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    assert is_available() is True


def test_normalize_falls_back_to_input_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    text = 'Visit "/login"'
    assert normalize(text) == text
