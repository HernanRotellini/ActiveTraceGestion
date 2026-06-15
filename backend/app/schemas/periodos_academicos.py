"""Schemas Pydantic para períodos académicos."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ── PeriodoAcademico ─────────────────────────────────────────────


class PeriodoAcademicoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    fecha_inicio: date
    fecha_fin: date


class PeriodoAcademicoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None


class PeriodoFechaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    periodo_id: UUID
    key: str
    label: str
    fecha: date


class PeriodoProgramaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    periodo_id: UUID
    materia_id: UUID
    materia_nombre: str
    carrera: str
    anio: int
    activo: bool


class PeriodoAcademicoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    activo: bool
    fechas: list[PeriodoFechaItem] = []
    programas: list[PeriodoProgramaItem] = []


class PeriodosListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PeriodoAcademicoResponse]


# ── Sub-resource payloads ────────────────────────────────────────


class PeriodoFechaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    fecha: date


class PeriodoProgramaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    carrera: str
    anio: int
