"""Schemas Pydantic para el módulo de comunicaciones."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── Preview ──────────────────────────────────────────────────────


class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asunto: str = Field(..., min_length=1, max_length=255)
    cuerpo: str = Field(..., min_length=1)
    variables: dict[str, str] = Field(default_factory=dict)


class PreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asunto_renderizado: str
    cuerpo_renderizado: str


# ── Envío Masivo ─────────────────────────────────────────────────


class EnvioMasivoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    asunto: str = Field(..., min_length=1, max_length=255)
    cuerpo: str = Field(..., min_length=1)


class EnvioMasivoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: UUID
    mensajes_creados: int


# ── Lotes ────────────────────────────────────────────────────────


class LoteResumen(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: UUID
    materia_id: UUID
    total: int
    pendientes: int
    enviados: int
    errores: int
    cancelados: int
    created_at: datetime


class LotesListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[LoteResumen]
    total: int


# ── Comunicacion Detail ──────────────────────────────────────────


class ComunicacionDetail(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    materia_id: UUID
    destinatario: str
    asunto: str
    cuerpo: str
    estado: str
    lote_id: UUID
    enviado_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class LoteDetalleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: UUID
    materia_id: UUID
    comunicaciones: list[ComunicacionDetail]


# ── Acciones ─────────────────────────────────────────────────────


class AccionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje: str
    afectados: int
