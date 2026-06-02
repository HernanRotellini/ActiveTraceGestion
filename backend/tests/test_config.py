"""Tests para core/config.py — Settings tipado con Pydantic v2."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Remueve las vars de entorno que podrían contaminar el test."""
    vars_to_clear = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ENCRYPTION_KEY",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
    ]
    saved = {}
    for var in vars_to_clear:
        saved[var] = os.environ.pop(var, None)
    yield
    for var, val in saved.items():
        if val is not None:
            os.environ[var] = val
        else:
            os.environ.pop(var, None)


class TestSettingsValid:
    """Settings se instancia correctamente con entorno válido."""

    def test_minimal_valid_env(self, clean_env: None) -> None:
        """Variables mínimas válidas → Settings se instancia."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert settings.DATABASE_URL == "postgresql+asyncpg://u:p@localhost:5432/db"
        assert settings.SECRET_KEY == "a" * 32
        assert settings.ENCRYPTION_KEY == "b" * 32

    def test_access_token_default(self, clean_env: None) -> None:
        """ACCESS_TOKEN_EXPIRE_MINUTES default a 15 si no se provee."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15

    def test_access_token_custom(self, clean_env: None) -> None:
        """ACCESS_TOKEN_EXPIRE_MINUTES se puede sobrescribir."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
        settings = Settings(_env_file=None)  # type: ignore[call-arg]
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


class TestSettingsInvalid:
    """Settings falla con entorno inválido o incompleto."""

    def test_missing_database_url(self, clean_env: None) -> None:
        """Sin DATABASE_URL → ValidationError."""
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]

    def test_short_secret_key(self, clean_env: None) -> None:
        """SECRET_KEY < 32 caracteres → ValidationError."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "short"  # menos de 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]

    def test_wrong_encryption_key_length(self, clean_env: None) -> None:
        """ENCRYPTION_KEY ≠ 32 caracteres → ValidationError."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "wrong-length"
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]

    def test_invalid_token_type(self, clean_env: None) -> None:
        """ACCESS_TOKEN_EXPIRE_MINUTES no-numérico → ValidationError."""
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://u:p@localhost:5432/db"
        os.environ["SECRET_KEY"] = "a" * 32
        os.environ["ENCRYPTION_KEY"] = "b" * 32
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "not-a-number"
        with pytest.raises(ValidationError):
            Settings(_env_file=None)  # type: ignore[call-arg]
