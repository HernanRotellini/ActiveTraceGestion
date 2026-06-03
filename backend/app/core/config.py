"""Configuración tipada del sistema vía Pydantic v2 + pydantic-settings.

Toda la configuración se carga desde variables de entorno (y archivo .env).
Un valor inválido o ausente en variables requeridas impide el arranque.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings tipados con Pydantic v2.

    Carga desde variables de entorno y/o archivo .env en el directorio de trabajo.
    Las variables REQUERIDAS son:
      - DATABASE_URL
      - SECRET_KEY   (mínimo 32 caracteres)
      - ENCRYPTION_KEY (exactamente 32 caracteres)
    ACCESS_TOKEN_EXPIRE_MINUTES tiene default 15 y es opcional.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    # ── Requeridas ──────────────────────────────────────────────
    DATABASE_URL: str = Field(min_length=1)

    # ── JWT ─────────────────────────────────────────────────────
    SECRET_KEY: str = Field(min_length=32)

    # ── AES-256 para PII en reposo ──────────────────────────────
    ENCRYPTION_KEY: str = Field(min_length=32, max_length=32)

    # ── Opcionales con default ──────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1)

    # ── OpenTelemetry (opcional) ────────────────────────────────
    OTEL_SERVICE_NAME: str = Field(default="activia-trace")
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(default=None)

    # ── Moodle Web Services (opcional por tenant) ──────────────
    MOODLE_BASE_URL: str | None = Field(default=None)
    MOODLE_TOKEN: str | None = Field(default=None)

    # ── Validaciones adicionales ────────────────────────────────

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def encryption_key_must_be_32_chars(cls, v: str) -> str:
        """Valida que ENCRYPTION_KEY tenga exactamente 32 caracteres."""
        if len(v) != 32:
            raise ValueError(
                f"ENCRYPTION_KEY debe tener exactamente 32 caracteres, "
                f"tiene {len(v)}"
            )
        return v
