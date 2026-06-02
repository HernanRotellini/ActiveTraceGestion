"""Schemas Pydantic para RBAC."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    codigo: str
    nombre: str
    created_at: datetime
    updated_at: datetime


class PermisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    codigo: str
    nombre: str
    modulo: str
    accion: str
    created_at: datetime
    updated_at: datetime


class RolPermisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    rol_id: UUID
    permiso_id: UUID
    habilitado: bool
    alcance: str
    created_at: datetime
    updated_at: datetime
