"""Modelos RBAC: roles, permisos y asignaciones tenant-scoped."""

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class Rol(TenantScopedMixin, Base):
    __tablename__ = "roles"

    codigo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)


class Permiso(TenantScopedMixin, Base):
    __tablename__ = "permisos"

    codigo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    modulo: Mapped[str] = mapped_column(String(100), nullable=False)
    accion: Mapped[str] = mapped_column(String(100), nullable=False)


class RolPermiso(TenantScopedMixin, Base):
    __tablename__ = "roles_permisos"

    rol_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, index=True)
    permiso_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("permisos.id"), nullable=False, index=True)
    habilitado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    alcance: Mapped[str] = mapped_column(String(20), nullable=False, default="global", server_default="global")
