"""Modelos de calificaciones y umbral de aprobación."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin

import enum


class OrigenCalificacion(str, enum.Enum):
    IMPORTADO = "Importado"
    MANUAL = "Manual"


class Calificacion(TenantScopedMixin, Base):
    __tablename__ = "calificaciones"

    entrada_padron_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("entradas_padron.id"),
        nullable=False,
        index=True,
    )
    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    actividad: Mapped[str] = mapped_column(String(255), nullable=False)
    nota_numerica: Mapped[float | None] = mapped_column(Float, nullable=True)
    nota_textual: Mapped[str | None] = mapped_column(String(255), nullable=True)
    aprobado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    origen: Mapped[OrigenCalificacion] = mapped_column(
        Enum(OrigenCalificacion, name="origen_calificacion", create_constraint=True),
        nullable=False,
    )
    importado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "materia_id", "entrada_padron_id", "actividad",
            name="uq_calificacion_actividad",
        ),
    )


class UmbralMateria(TenantScopedMixin, Base):
    __tablename__ = "umbrales_materia"

    asignacion_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("asignaciones.id"),
        nullable=False,
        index=True,
    )
    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    umbral_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    valores_aprobatorios: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "asignacion_id", "materia_id",
            name="uq_umbral_asignacion_materia",
        ),
    )
