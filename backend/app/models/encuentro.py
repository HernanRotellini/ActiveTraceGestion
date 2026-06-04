"""Modelos de encuentros sincrónicos: slots de recurrencia e instancias concretas."""

import enum
from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class DiaSemana(str, enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miercoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sabado"


class EstadoInstancia(str, enum.Enum):
    PROGRAMADO = "Programado"
    REALIZADO = "Realizado"
    CANCELADO = "Cancelado"


class SlotEncuentro(TenantScopedMixin, Base):
    __tablename__ = "slots_encuentro"

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
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    dia_semana: Mapped[DiaSemana] = mapped_column(
        Enum(DiaSemana, name="dia_semana", create_constraint=True),
        nullable=False,
    )
    hora: Mapped[time] = mapped_column(Time, nullable=False)
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    cant_semanas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fecha_unica: Mapped[date | None] = mapped_column(Date, nullable=True)
    meet_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    vig_desde: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    vig_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InstanciaEncuentro(TenantScopedMixin, Base):
    __tablename__ = "instancias_encuentro"

    slot_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("slots_encuentro.id"),
        nullable=True,
        index=True,
    )
    materia_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("materias.id"),
        nullable=False,
        index=True,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hora: Mapped[time] = mapped_column(Time, nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoInstancia] = mapped_column(
        Enum(EstadoInstancia, name="estado_instancia", create_constraint=True),
        nullable=False,
        default=EstadoInstancia.PROGRAMADO,
    )
    meet_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
