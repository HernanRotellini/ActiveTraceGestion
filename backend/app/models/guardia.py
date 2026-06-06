"""Modelo de guardias de atención tutorial."""

import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text, Time
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


class EstadoGuardia(str, enum.Enum):
    PENDIENTE = "Pendiente"
    REALIZADA = "Realizada"
    CANCELADA = "Cancelada"


class Guardia(TenantScopedMixin, Base):
    __tablename__ = "guardias"

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
    carrera_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("carreras.id"),
        nullable=False,
        index=True,
    )
    cohorte_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("cohortes.id"),
        nullable=False,
        index=True,
    )
    dia: Mapped[DiaSemana] = mapped_column(
        Enum(DiaSemana, name="dia_semana_guardia", create_constraint=True),
        nullable=False,
    )
    horario: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[EstadoGuardia] = mapped_column(
        Enum(EstadoGuardia, name="estado_guardia", create_constraint=True),
        nullable=False,
        default=EstadoGuardia.PENDIENTE,
    )
    comentarios: Mapped[str | None] = mapped_column(Text, nullable=True)
