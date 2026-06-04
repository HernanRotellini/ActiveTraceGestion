"""Schemas Pydantic para calificaciones y umbral de materia."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ── Calificacion ────────────────────────────────────────────────


class CalificacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    materia_id: UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None


class CalificacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    entrada_padron_id: UUID
    materia_id: UUID
    actividad: str
    nota_numerica: float | None = None
    nota_textual: str | None = None
    aprobado: bool
    origen: str
    importado_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CalificacionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CalificacionResponse]
    total: int


# ── UmbralMateria ───────────────────────────────────────────────


class UmbralMateriaCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    umbral_pct: int = 60
    valores_aprobatorios: list[str] = ["Satisfactorio", "Supera lo esperado"]


class UmbralMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    umbral_pct: int | None = None
    valores_aprobatorios: list[str] | None = None


class UmbralMateriaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    tenant_id: UUID
    asignacion_id: UUID
    materia_id: UUID
    umbral_pct: int
    valores_aprobatorios: list[str] | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


# ── Import Preview ──────────────────────────────────────────────


class DetectedActivity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str
    tipo: str  # "numeric" | "textual"


class StudentMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entrada_padron_id: UUID
    nombre: str
    apellidos: str
    email: str
    datos: dict[str, str | float | None]


class UnmatchedRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fila: int
    datos: dict[str, str]


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str
    materia_id: UUID
    cohorte_id: UUID
    actividades: list[DetectedActivity]
    total_rows: int
    alumnos_match: list[StudentMatch]
    alumnos_no_match: list[UnmatchedRow]


class ImportConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str
    actividad_ids: list[str]


class ImportConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    cohorte_id: UUID
    registros_creados: int
    actividades_importadas: list[str]


# ── Completion Report ───────────────────────────────────────────


class PosibleEntregaSinCorregir(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_nombre: str
    alumno_apellidos: str
    actividad: str


class CompletionReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: UUID
    cohorte_id: UUID
    posibles_entregas_sin_corregir: list[PosibleEntregaSinCorregir]
