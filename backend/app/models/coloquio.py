"""Modelos de evaluaciones y coloquios con soporte multi-tenant."""

import enum
from datetime import date, time
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TenantScopedMixin


class TipoEvaluacion(str, enum.Enum):
    PARCIAL = "Parcial"
    TP = "TP"
    COLOQUIO = "Coloquio"
    RECUPERATORIO = "Recuperatorio"


class EstadoEvaluacion(str, enum.Enum):
    ACTIVA = "Activa"
    CERRADA = "Cerrada"


class EstadoReserva(str, enum.Enum):
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"


class Evaluacion(TenantScopedMixin, Base):
    __tablename__ = "evaluaciones"

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
    tipo: Mapped[TipoEvaluacion] = mapped_column(
        Enum(TipoEvaluacion, name="tipo_evaluacion", create_constraint=True),
        nullable=False,
    )
    instancia: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[EstadoEvaluacion] = mapped_column(
        Enum(EstadoEvaluacion, name="estado_evaluacion", create_constraint=True),
        nullable=False,
        default=EstadoEvaluacion.ACTIVA,
    )


class TurnoEvaluacion(TenantScopedMixin, Base):
    __tablename__ = "turnos_evaluacion"

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("evaluaciones.id"),
        nullable=False,
        index=True,
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora_inicio: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_fin: Mapped[time | None] = mapped_column(Time, nullable=True)
    cupo_maximo: Mapped[int] = mapped_column(Integer, nullable=False)
    cupo_restante: Mapped[int] = mapped_column(Integer, nullable=False)


class ReservaEvaluacion(TenantScopedMixin, Base):
    __tablename__ = "reservas_evaluacion"

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("evaluaciones.id"),
        nullable=False,
        index=True,
    )
    turno_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("turnos_evaluacion.id"),
        nullable=False,
        index=True,
    )
    alumno_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    estado: Mapped[EstadoReserva] = mapped_column(
        Enum(EstadoReserva, name="estado_reserva", create_constraint=True),
        nullable=False,
        default=EstadoReserva.ACTIVA,
    )


class ResultadoEvaluacion(TenantScopedMixin, Base):
    __tablename__ = "resultados_evaluacion"

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("evaluaciones.id"),
        nullable=False,
        index=True,
    )
    alumno_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
    nota_final: Mapped[str] = mapped_column(Text, nullable=False)
    registrado_por: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
    )


class ConvocatoriaAlumno(TenantScopedMixin, Base):
    __tablename__ = "convocatorias_alumnos"

    evaluacion_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("evaluaciones.id"),
        nullable=False,
        index=True,
    )
    alumno_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("usuarios.id"),
        nullable=False,
        index=True,
    )
