"""Modelos de estructura académica: Carrera, Cohorte, Materia."""

from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class Carrera(TenantScopedMixin, Base):
    __tablename__ = "carreras"

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activa", server_default="activa")
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False, default="", server_default="")


class Cohorte(TenantScopedMixin, Base):
    __tablename__ = "cohortes"

    carrera_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("carreras.id"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    vig_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vig_hasta: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activa", server_default="activa")


class Materia(TenantScopedMixin, Base):
    __tablename__ = "materias"

    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="activa", server_default="activa")
    carrera_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("carreras.id"), nullable=True, index=True)
    cohorte_id: Mapped[UUID | None] = mapped_column(PostgresUUID(as_uuid=True), ForeignKey("cohortes.id"), nullable=True, index=True)
    carga_horaria: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class PeriodoAcademico(TenantScopedMixin, Base):
    """Período académico: agrupa fechas y programas de un cuatrimestre."""

    __tablename__ = "periodos_academicos"

    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)
    activo: Mapped[bool] = mapped_column(nullable=False, default=False)


class PeriodoFecha(TenantScopedMixin, Base):
    """Fecha académica dentro de un período (key+label+date)."""

    __tablename__ = "periodos_fechas"

    periodo_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("periodos_academicos.id"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)


class PeriodoPrograma(TenantScopedMixin, Base):
    """Programa (materia) dentro de un período académico."""

    __tablename__ = "periodos_programas"

    periodo_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("periodos_academicos.id"),
        nullable=False,
        index=True,
    )
    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    carrera: Mapped[str] = mapped_column(String(255), nullable=False)
    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(nullable=False, default=True)
