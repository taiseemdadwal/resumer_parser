"""Tests for dotenv compatibility in CLI bootstrap."""

from __future__ import annotations

from pathlib import Path

from app import main as main_module


def test_load_env_file_sets_missing_variables(monkeypatch, tmp_path: Path) -> None:
    """Dotenv loader should set vars from file when not already in environment."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (tmp_path / ".env").write_text("OPENAI_API_KEY=abc123\n", encoding="utf-8")

    main_module._load_env_file()

    assert main_module.os.getenv("OPENAI_API_KEY") == "abc123"


def test_load_env_file_does_not_override_existing_env(monkeypatch, tmp_path: Path) -> None:
    """Explicitly exported environment variables should take precedence over dotenv."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENAI_MODEL", "manual-model")
    (tmp_path / ".env").write_text("OPENAI_MODEL=file-model\n", encoding="utf-8")

    main_module._load_env_file()

    assert main_module.os.getenv("OPENAI_MODEL") == "manual-model"


def test_load_env_file_ignores_malformed_lines(monkeypatch, tmp_path: Path) -> None:
    """Malformed dotenv lines should be ignored without raising exceptions."""

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GOOD_KEY", raising=False)
    (tmp_path / ".env").write_text("NOT_VALID\n=bad\nGOOD_KEY=value\n", encoding="utf-8")

    main_module._load_env_file()

    assert main_module.os.getenv("GOOD_KEY") == "value"
