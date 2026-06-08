"""Schemas Pydantic para panel de auditoría y métricas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccionesPorDiaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    fecha: datetime
    total: int


class AccionesPorDiaListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[AccionesPorDiaResponse]


class ComunicacionesPorDocenteResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    docente_id: UUID
    accion: str
    total: int


class ComunicacionesPorDocenteListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ComunicacionesPorDocenteResponse]


class InteraccionesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    docente_id: UUID
    materia_id: UUID | None = None
    accion: str
    total: int


class InteraccionesListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[InteraccionesResponse]


class UltimasAccionesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    fecha_hora: datetime
    actor_id: UUID
    impersonado_id: UUID | None = None
    materia_id: UUID | None = None
    accion: str
    detalle: dict | None = None
    filas_afectadas: int | None = None
    ip: str | None = None
    user_agent: str | None = None


class UltimasAccionesListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[UltimasAccionesResponse]
