"""Schemas Pydantic para el módulo de evaluaciones y coloquios."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TurnoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fecha: date
    hora_inicio: time | None = None
    hora_fin: time | None = None
    cupo_maximo: int = Field(..., gt=0)
    cupo_restante: int | None = None


class EvaluacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    cohorte_id: UUID
    tipo: str
    instancia: str = Field(..., min_length=1, max_length=255)
    turnos: list[TurnoCreate] = Field(..., min_length=1)


class TurnoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    fecha: date
    hora_inicio: time | None = None
    hora_fin: time | None = None
    cupo_maximo: int
    cupo_restante: int


class EvaluacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    cohorte_id: UUID
    tipo: str
    instancia: str
    estado: str
    turnos: list[TurnoResponse] = []
    created_at: datetime
    updated_at: datetime


class EvaluacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    cohorte_id: UUID
    tipo: str
    instancia: str
    estado: str
    total_turnos: int = 0
    alumnos_convocados: int = 0
    reservas_activas: int = 0
    cupos_libres: int = 0
    created_at: datetime


class ReservaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    turno_id: UUID
    alumno_id: UUID
    estado: str
    created_at: datetime


class ImportarAlumnosRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_ids: list[UUID] = Field(..., min_length=1)


class ImportarAlumnosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    importados: int


class ResultadoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_id: UUID
    nota_final: str = Field(..., min_length=1)


class ResultadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    alumno_id: UUID
    nota_final: str
    registrado_por: UUID
    created_at: datetime
    updated_at: datetime


class MetricasResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumnos_convocados: int
    convocatorias_activas: int
    reservas_activas: int
    notas_registradas: int


class MensajeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str


class AgendaReservaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evaluacion_id: UUID
    turno_id: UUID
    fecha: date | None = None
    alumno_id: UUID
    created_at: datetime


class AgendaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AgendaReservaResponse]
    total: int


class ResultadosConsolidadosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ResultadoResponse]
    total: int
