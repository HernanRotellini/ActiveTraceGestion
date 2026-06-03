"""Schemas Pydantic para Asignacion."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field


class AsignacionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: UUID
    rol: str
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: UUID | None = None
    desde: date
    hasta: date | None = None


class AsignacionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rol: str | None = None
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: UUID | None = None
    desde: date | None = None
    hasta: date | None = None


class AsignacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    usuario_id: UUID
    rol: str
    materia_id: UUID | None = None
    carrera_id: UUID | None = None
    cohorte_id: UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: UUID | None = None
    desde: date
    hasta: date | None = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def estado_vigencia(self) -> str:
        from datetime import date as d
        today = d.today()
        if self.hasta is not None and self.hasta < today:
            return "vencida"
        return "vigente"
