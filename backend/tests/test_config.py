"""Tests for config/settings."""
import os


def test_config_defaults():
    from app.config import Settings
    s = Settings()
    assert s.ALGORITHM == "HS256"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 60
    assert "sqlite" in s.DATABASE_URL
    assert s.STRIPE_WEBHOOK_SECRET is not None


def test_config_reads_from_env(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "env-test-secret")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    from app.config import Settings
    s = Settings()
    assert s.SECRET_KEY == "env-test-secret"
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 120
