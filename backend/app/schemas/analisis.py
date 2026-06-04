"""Schemas Pydantic para análisis de calificaciones y reportes."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActividadAtrasada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actividad: str
    motivo: str


class AtrasadosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    alumno_nombre: str
    actividades_atrasadas: list[ActividadAtrasada]


class RankingItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ranking: int
    entrada_padron_id: UUID
    alumno_nombre: str
    actividades_aprobadas: int


class RankingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[RankingItem]
    total: int


class DesgloseActividad(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actividad: str
    presentado: int
    promedio: float | None = None
    min: float | None = None
    max: float | None = None


class ReportesRapidosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_alumnos: int
    total_calificaciones: int
    promedio_general: float
    total_aprobados: int
    total_no_aprobados: int
    desglose_por_actividad: list[DesgloseActividad]


class NotaFinalItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    alumno_nombre: str
    promedio: float
    aprobado: bool


class NotasFinalesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[NotaFinalItem]
    total: int


class TPSinCorregirItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_nombre: str
    actividad: str
    materia_id: UUID


class ExportarTpsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[TPSinCorregirItem]
    total: int


class MonitorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    alumno_nombre: str
    email: str
    regional: str | None = None
    comision: str | None = None
    total_actividades: int
    aprobadas: int
    pendientes: int
    atrasado: bool


class MonitorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MonitorItem]
    total: int
