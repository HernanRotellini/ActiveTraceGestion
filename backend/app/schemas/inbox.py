"""Schemas Pydantic para mensajería interna (inbox)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CrearHiloRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asunto: str = Field(min_length=1, max_length=255)
    destinatarios: list[UUID] = Field(min_length=1)
    cuerpo: str = Field(min_length=1)


class ResponderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cuerpo: str = Field(min_length=1)


class MensajeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    hilo_id: UUID
    remitente_id: UUID
    cuerpo: str
    created_at: datetime


class HiloResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    asunto: str
    participantes_ids: list
    ultimo_mensaje_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    mensajes: list[MensajeResponse] | None = None
    ultimo_mensaje: str | None = None


class HiloListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[HiloResponse]
    total: int
