import pytest
from pydantic import ValidationError

from app.core.config import Settings


DATABASE_DEFAULTS = {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/weather",
    "POSTGRES_USER": "test",
    "POSTGRES_PASSWORD": "test",
    "POSTGRES_DB": "test",
    "POSTGRES_PORT": "5432",
}


@pytest.fixture(autouse=True)
def isolated_settings_env(monkeypatch):
    for field_name in Settings.model_fields:
        monkeypatch.delenv(field_name, raising=False)
        monkeypatch.delenv(field_name.lower(), raising=False)

    monkeypatch.setitem(Settings.model_config, "env_file", None)

    # Required database settings stay out of the way of the assertions below.
    for name, value in DATABASE_DEFAULTS.items():
        monkeypatch.setenv(name, value)


def test_production_debug_true_raises_error():
    with pytest.raises(
        ValidationError,
        match="DEBUG must be false in production",
    ):
        Settings(
            APP_ENV="production",
            DEBUG=True,
        )


def test_production_debug_false_is_valid():
    settings = Settings(
        APP_ENV="production",
        DEBUG=False,
    )

    assert settings.DEBUG is False


def test_development_debug_true_is_valid():
    settings = Settings(
        APP_ENV="development",
        DEBUG=True,
    )

    assert settings.DEBUG is True


def test_settings_read_environment_variables(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("HTTP_TIMEOUT", "20.5")

    settings = Settings()

    assert settings.APP_ENV == "production"
    assert settings.DEBUG is False
    assert settings.LOG_LEVEL == "WARNING"
    assert settings.HTTP_TIMEOUT == 20.5


def test_settings_reject_invalid_app_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("APP_ENV",)
    assert errors[0]["type"] == "literal_error"


def test_settings_reject_invalid_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "TRACE")

    with pytest.raises(ValidationError) as exc_info:
        Settings()

    errors = exc_info.value.errors()

    assert len(errors) == 1
    assert errors[0]["loc"] == ("LOG_LEVEL",)
    assert errors[0]["type"] == "literal_error"

