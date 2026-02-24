"""Offline-safe tests for optional OpenAI client adapter."""

from __future__ import annotations

import pytest

from app.extractors.openai_llm_client import OpenAILLMClient


def test_openai_client_raises_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client should fail fast before any SDK call when API key is missing."""

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Missing OpenAI API key"):
        OpenAILLMClient(model="gpt-4o-mini", api_key=None)
