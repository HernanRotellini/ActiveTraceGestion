"""Schemas Pydantic para operaciones de equipo docente."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AsignacionMasivaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_ids: list[UUID]
    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    rol: str
    desde: date
    hasta: date | None = None


class EquipoOrigen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID


class EquipoDestino(BaseModel):
    model_config = ConfigDict(extra="forbid")

    carrera_id: UUID
    cohorte_id: UUID
    desde: date
    hasta: date | None = None


class CloneEquipoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    origen: EquipoOrigen
    destino: EquipoDestino


class VigenciaUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    carrera_id: UUID
    cohorte_id: UUID
    desde: date | None = None
    hasta: date | None = None


class VigenciaUpdateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignaciones_afectadas: int
