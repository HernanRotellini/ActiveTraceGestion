"""Schemas Pydantic para padrón de alumnos."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VersionPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: str
    materia_id: str
    cohorte_id: str
    cargado_por: str
    cargado_at: datetime
    activa: bool
    created_at: datetime
    updated_at: datetime


class VersionPadronList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[VersionPadronResponse]
    total: int
    page: int
    size: int


class EntradaPadronResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: str
    version_id: str
    usuario_id: str | None = None
    nombre: str
    apellidos: str
    email: str
    comision: str
    regional: str | None = None
    created_at: datetime
    updated_at: datetime


class EntradaPadronList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[EntradaPadronResponse]
    total: int
    page: int
    size: int


class ColumnaDetectada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    mapeo: str  # nombre, apellidos, email, comision, regional


class FilaPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fila: int
    datos: dict[str, str]


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str
    columnas_detectadas: list[ColumnaDetectada]
    filas_preview: list[FilaPreview]
    total_filas: int
    materia_id: str
    cohorte_id: str


class ImportConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str = Field(min_length=1)


class ImportConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: str
    materia_id: str
    cohorte_id: str
    entry_count: int


class VaciarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: str
    affected_count: int
