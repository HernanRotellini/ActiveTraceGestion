"""Schemas Pydantic para el módulo de avisos institucionales."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AvisoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: str
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: str = "Info"
    titulo: str = Field(..., min_length=1, max_length=200)
    cuerpo: str = Field(..., min_length=1)
    inicio_en: datetime
    fin_en: datetime | None = None
    orden: int = Field(default=0, ge=0)
    activo: bool = True
    requiere_ack: bool = False

    @field_validator("alcance")
    @classmethod
    def validate_alcance(cls, v: str) -> str:
        allowed = {"Global", "PorMateria", "PorCohorte", "PorRol"}
        if v not in allowed:
            raise ValueError(f"alcance must be one of {allowed}")
        return v

    @field_validator("severidad")
    @classmethod
    def validate_severidad(cls, v: str) -> str:
        allowed = {"Info", "Advertencia", "Critico"}
        if v not in allowed:
            raise ValueError(f"severidad must be one of {allowed}")
        return v

    @field_validator("materia_id")
    @classmethod
    def validate_materia_id(cls, v: UUID | None, info) -> UUID | None:
        if info.data.get("alcance") == "PorMateria" and v is None:
            raise ValueError("materia_id is required when alcance is PorMateria")
        return v

    @field_validator("cohorte_id")
    @classmethod
    def validate_cohorte_id(cls, v: UUID | None, info) -> UUID | None:
        if info.data.get("alcance") == "PorCohorte" and v is None:
            raise ValueError("cohorte_id is required when alcance is PorCohorte")
        return v

    @field_validator("rol_destino")
    @classmethod
    def validate_rol_destino(cls, v: str | None, info) -> str | None:
        if info.data.get("alcance") == "PorRol" and v is None:
            raise ValueError("rol_destino is required when alcance is PorRol")
        return v


class AvisoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alcance: str | None = None
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: str | None = None
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    cuerpo: str | None = Field(default=None, min_length=1)
    inicio_en: datetime | None = None
    fin_en: datetime | None = None
    orden: int | None = Field(default=None, ge=0)
    activo: bool | None = None
    requiere_ack: bool | None = None

    @field_validator("alcance")
    @classmethod
    def validate_alcance(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"Global", "PorMateria", "PorCohorte", "PorRol"}
            if v not in allowed:
                raise ValueError(f"alcance must be one of {allowed}")
        return v

    @field_validator("severidad")
    @classmethod
    def validate_severidad(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"Info", "Advertencia", "Critico"}
            if v not in allowed:
                raise ValueError(f"severidad must be one of {allowed}")
        return v


class AvisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    alcance: str
    materia_id: UUID | None = None
    cohorte_id: UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime | None = None
    orden: int
    activo: bool
    requiere_ack: bool
    created_at: datetime
    updated_at: datetime


class AvisoListResponse(BaseModel):
    """Versión resumida para listados públicos (sin cuerpo completo)."""
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    alcance: str
    severidad: str
    titulo: str
    inicio_en: datetime
    fin_en: datetime | None = None
    orden: int
    requiere_ack: bool
    created_at: datetime


class AckCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Empty body — aviso_id viene del path parameter


class AckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    aviso_id: UUID
    usuario_id: UUID
    confirmado_at: datetime


class AvisoStatsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_acks: int
    usuarios_sin_confirmar: list[UUID] | None = None
