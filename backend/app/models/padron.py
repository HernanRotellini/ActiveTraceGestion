"""Modelos de padrón de alumnos versionado."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class VersionPadron(TenantScopedMixin, Base):
    """Versión del padrón de alumnos para una materia×cohorte.

    Cada carga genera una nueva versión. Solo una versión puede estar
    activa por combinación (materia_id, cohorte_id).
    """

    __tablename__ = "versiones_padron"

    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    cohorte_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("cohortes.id"),
        nullable=False,
        index=True,
    )
    cargado_por: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
    )
    cargado_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )


class EntradaPadron(TenantScopedMixin, Base):
    """Entrada individual del padrón: un alumno en una versión."""

    __tablename__ = "entradas_padron"

    version_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("versiones_padron.id"),
        nullable=False,
        index=True,
    )
    usuario_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=True,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    comision: Mapped[str] = mapped_column(String(50), nullable=False)
    regional: Mapped[str | None] = mapped_column(String(100), nullable=True)
