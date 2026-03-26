"""Unit tests for config module."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings


def test_settings_defaults():
    """Test that default settings are applied correctly."""
    settings = Settings()
    assert settings.host == "0.0.0.0"
    assert settings.port == 3000
    assert settings.reload is False
    assert settings.static_dir == Path("/app/static")
    assert settings.static_url == "/static"
    assert settings.cors_origins == ["*"]


def test_settings_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("HOST", "127.0.0.1")
    monkeypatch.setenv("PORT", "8080")
    monkeypatch.setenv("RELOAD", "true")
    monkeypatch.setenv("STATIC_DIR", "/custom/static")

    settings = Settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8080
    assert settings.reload is True
    assert settings.static_dir == Path("/custom/static")


def test_settings_static_dir_path():
    """Test that static_dir is properly converted to Path."""
    settings = Settings(static_dir="/custom/path")
    assert isinstance(settings.static_dir, Path)
    assert settings.static_dir == Path("/custom/path")


def test_settings_cors_origins_list():
    """Test that CORS origins are properly parsed as list."""
    settings = Settings(cors_origins=["http://localhost:3000", "https://example.com"])
    assert len(settings.cors_origins) == 2
    assert "http://localhost:3000" in settings.cors_origins


def test_get_settings_returns_cached():
    """Test that get_settings returns the same cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_config_loads_from_env(monkeypatch):
    """Test config loads values from environment variables."""
    monkeypatch.setenv("PORT", "9000")
    monkeypatch.setenv("HOST", "localhost")

    # Clear the cached settings
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.port == 9000
    assert settings.host == "localhost"
