import pytest
from src.config import Settings, get_settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.env == "development"
        assert settings.log_level == "INFO"
        assert settings.static_dir == "static"
        assert settings.allowed_hosts == ["*"]
    
    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ENV", "production")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        settings = Settings()
        assert settings.env == "production"
        assert settings.log_level == "WARNING"
    
    def test_get_settings_returns_cached(self):
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
