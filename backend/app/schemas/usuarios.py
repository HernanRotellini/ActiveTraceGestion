"""Schemas Pydantic para Usuario."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    apellidos: str
    email: str
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    legajo: str | None = None
    banco: str | None = None
    facturador: bool = False


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    apellidos: str | None = None
    email: str | None = None
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    legajo: str | None = None
    banco: str | None = None
    facturador: bool | None = None
    estado: str | None = None


class UsuarioResponse(BaseModel):
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
    created_at: datetime
    updated_at: datetime
