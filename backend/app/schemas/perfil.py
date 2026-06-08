"""Schemas Pydantic para perfil propio del usuario autenticado."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PerfilUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    apellidos: str | None = None
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    banco: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    regional: str | None = None
    modalidad_cobro: str | None = None
    genero: str | None = None
    condicion_impositiva: str | None = None
    matricula_profesional: str | None = None


class PerfilResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    nombre: str
    apellidos: str
    email: str
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    estado: str
    legajo: str | None = None
    banco: str | None = None
    facturador: bool
    regional: str | None = None
    modalidad_cobro: str | None = None
    genero: str | None = None
    condicion_impositiva: str | None = None
    matricula_profesional: str | None = None
    created_at: datetime
    updated_at: datetime
