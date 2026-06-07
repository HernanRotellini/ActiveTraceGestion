"""Schemas Pydantic para tareas internas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarea import EstadoTarea


class TareaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: str = Field(..., min_length=1)
    asignado_a: UUID
    materia_id: UUID | None = None
    contexto_id: UUID | None = None


class TareaDelegate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignado_a: UUID


class TareaStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: EstadoTarea


class ComentarioTareaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    texto: str = Field(..., min_length=1)


class ComentarioTareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tarea_id: UUID
    autor_id: UUID
    texto: str
    created_at: datetime


class TareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    titulo: str
    descripcion: str
    estado: EstadoTarea
    asignado_a: UUID
    asignado_por: UUID
    materia_id: UUID | None = None
    contexto_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class TareaDetailResponse(TareaResponse):
    comentarios: list[ComentarioTareaResponse] = Field(default_factory=list)
