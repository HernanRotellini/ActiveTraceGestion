"""Modelos de autenticación tenant-scoped."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from app.core.database import Base
from app.models.base import TenantScopedMixin


class AuthUser(TenantScopedMixin, Base):
    """Usuario mínimo para autenticación propia."""

    __tablename__ = "auth_users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class RefreshSession(TenantScopedMixin, Base):
    """Refresh token opaco hasheado y rotado server-side."""

    __tablename__ = "refresh_sessions"

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("auth_users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_to_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), nullable=True)


class TotpFactor(TenantScopedMixin, Base):
    """Secreto TOTP cifrado, pendiente o habilitado."""

    __tablename__ = "totp_factors"

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("auth_users.id"), nullable=False, index=True)
    encrypted_secret: Mapped[str] = mapped_column(String(512), nullable=False)
    enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TwoFactorChallenge(TenantScopedMixin, Base):
    """Challenge temporal para completar login con segundo factor."""

    __tablename__ = "two_factor_challenges"

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("auth_users.id"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PasswordRecoveryToken(TenantScopedMixin, Base):
    """Token de recuperación hasheado, corto y de un solo uso."""

    __tablename__ = "password_recovery_tokens"

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("auth_users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
