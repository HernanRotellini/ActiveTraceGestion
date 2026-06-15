"""Schemas Pydantic para estructura académica."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field


# ── Carrera ─────────────────────────────────────────────────────


class CarreraCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str
    nombre: str
    descripcion: str | None = None


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str | None = None
    nombre: str | None = None
    descripcion: str | None = None
    estado: str | None = None


class CarreraResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    codigo: str
    nombre: str
    estado: str
    created_at: datetime
    updated_at: datetime
    descripcion: str = ""

    @computed_field
    @property
    def activo(self) -> bool:
        return self.estado == "activa"

    @computed_field
    @property
    def creada_en(self) -> datetime:
        return self.created_at


# ── Cohorte ─────────────────────────────────────────────────────


class CohorteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carrera_id: UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None


class CohorteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    carrera_id: UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None
    estado: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def activo(self) -> bool:
        return self.estado == "activa"

    @computed_field
    @property
    def creada_en(self) -> datetime:
        return self.created_at


# ── Materia ─────────────────────────────────────────────────────


class MateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str
    nombre: str


class MateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    codigo: str | None = None
    carga_horaria: int | None = None
    estado: str | None = None


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None


class MateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    codigo: str
    nombre: str
    estado: str
    created_at: datetime
    updated_at: datetime
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    carga_horaria: int = 0
    carrera_nombre: str | None = None
    cohorte_nombre: str | None = None

    @computed_field
    @property
    def activo(self) -> bool:
        return self.estado == "activa"

    @computed_field
    @property
    def creada_en(self) -> datetime:
        return self.created_at
