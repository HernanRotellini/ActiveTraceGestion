"""Modelos ORM para programas de materia y fechas académicas."""

import enum
from datetime import date
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class TipoFechaAcademica(str, enum.Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class ProgramaMateria(TenantScopedMixin, Base):
    __tablename__ = "programa_materia"

    materia_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("materias.id"), nullable=False, index=True)
    carrera_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("carreras.id"), nullable=False, index=True)
    cohorte_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    referencia_archivo: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (
        Index("ix_programa_tenant_materia", "tenant_id", "materia_id"),
        Index("ix_programa_tenant_carrera", "tenant_id", "carrera_id"),
        Index("ix_programa_tenant_cohorte", "tenant_id", "cohorte_id"),
        Index("ix_programa_tenant_titulo", "tenant_id", "titulo"),
        Index("uq_programa_materia_tenant_contexto", "tenant_id", "materia_id", "carrera_id", "cohorte_id", "titulo", unique=True, postgresql_where=text("deleted_at IS NULL")),
    )


class FechaAcademica(TenantScopedMixin, Base):
    __tablename__ = "fecha_academica"

    materia_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("materias.id"), nullable=False, index=True)
    cohorte_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=False, index=True)
    tipo: Mapped[TipoFechaAcademica] = mapped_column(
        Enum(TipoFechaAcademica, name="tipo_fecha_academica", create_constraint=True, values_callable=lambda values: [item.value for item in values]),
        nullable=False,
    )
    numero: Mapped[int] = mapped_column(Integer, nullable=False)
    periodo: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        Index("ix_fecha_tenant_materia", "tenant_id", "materia_id"),
        Index("ix_fecha_tenant_cohorte", "tenant_id", "cohorte_id"),
        Index("ix_fecha_tenant_tipo", "tenant_id", "tipo"),
        Index("ix_fecha_tenant_periodo", "tenant_id", "periodo"),
        Index("ix_fecha_tenant_materia_cohorte", "tenant_id", "materia_id", "cohorte_id"),
        Index("ix_fecha_fecha", "tenant_id", "fecha"),
        Index("uq_fecha_academica_tenant_contexto", "tenant_id", "materia_id", "cohorte_id", "tipo", "numero", "periodo", unique=True, postgresql_where=text("deleted_at IS NULL")),
    )
