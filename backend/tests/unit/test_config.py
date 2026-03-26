import pytest
from src.config import Settings, get_settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.ENV == "development"
        assert settings.LOG_LEVEL == "INFO"
        assert settings.STATIC_DIR == "static"
        assert settings.ALLOWED_HOSTS == ["*"]
    
    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("ENV", "production")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        settings = Settings()
        assert settings.ENV == "production"
        assert settings.LOG_LEVEL == "WARNING"
    
    def test_get_settings_returns_cached(self):
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
