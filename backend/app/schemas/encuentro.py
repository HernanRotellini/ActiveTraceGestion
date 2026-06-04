"""Schemas Pydantic para el módulo de encuentros sincrónicos."""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SlotEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignacion_id: UUID
    materia_id: UUID
    titulo: str = Field(..., min_length=1, max_length=255)
    dia_semana: str
    hora: time
    fecha_inicio: date
    cant_semanas: int = Field(default=0, ge=0)
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: datetime
    vig_hasta: datetime | None = None


class SlotEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    asignacion_id: UUID
    materia_id: UUID
    titulo: str
    dia_semana: str
    hora: time
    fecha_inicio: date
    cant_semanas: int
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: datetime
    vig_hasta: datetime | None = None
    created_at: datetime
    updated_at: datetime


class InstanciaEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    fecha: date
    hora: time
    titulo: str = Field(..., min_length=1, max_length=255)
    meet_url: str | None = None


class InstanciaEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    estado: str | None = None
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None


class InstanciaEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    slot_id: UUID | None = None
    materia_id: UUID
    fecha: date
    hora: time
    titulo: str
    estado: str
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None
    created_at: datetime
    updated_at: datetime


class HtmlBlockResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    html: str
