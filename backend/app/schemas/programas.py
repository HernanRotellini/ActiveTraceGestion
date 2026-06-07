"""Schemas Pydantic para programas de materia y fechas académicas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.programas import TipoFechaAcademica


class ProgramaMateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    titulo: str = Field(..., max_length=200)
    referencia_archivo: str = Field(..., max_length=500)


class ProgramaMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, max_length=200)
    referencia_archivo: str | None = Field(default=None, max_length=500)


class ProgramaMateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    titulo: str
    referencia_archivo: str
    created_at: datetime


class FechaAcademicaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    cohorte_id: UUID
    tipo: TipoFechaAcademica
    numero: int = Field(..., ge=1, le=10)
    periodo: str = Field(..., max_length=50)
    fecha: date
    titulo: str = Field(..., max_length=255)


class FechaAcademicaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str | None = Field(default=None, max_length=255)
    fecha: date | None = None
    numero: int | None = Field(default=None, ge=1, le=10)
    periodo: str | None = Field(default=None, max_length=50)


class FechaAcademicaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    cohorte_id: UUID
    tipo: TipoFechaAcademica
    numero: int
    periodo: str
    fecha: date
    titulo: str
    created_at: datetime


class FechaAcademicaCalendarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    cohorte_id: UUID
    tipo: TipoFechaAcademica
    numero: int
    titulo: str
    fecha: date


class LMSFragmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contenido: str
