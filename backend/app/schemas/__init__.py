"""Schemas Pydantic del backend."""

from app.schemas.aviso import (
    AckCreate,
    AckResponse,
    AvisoCreate,
    AvisoListResponse,
    AvisoResponse,
    AvisoStatsResponse,
    AvisoUpdate,
)
from app.schemas.asignaciones import AsignacionCreate, AsignacionResponse, AsignacionUpdate
from app.schemas.equipos import (
    AsignacionMasivaRequest,
    CloneEquipoRequest,
    EquipoDestino,
    EquipoOrigen,
    VigenciaUpdateRequest,
    VigenciaUpdateResponse,
)
from app.schemas.padron import (
    ColumnaDetectada,
    EntradaPadronList,
    EntradaPadronResponse,
    FilaPreview,
    ImportConfirmRequest,
    ImportConfirmResponse,
    ImportPreviewResponse,
    VaciarResponse,
    VersionPadronList,
    VersionPadronResponse,
)
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse, UsuarioUpdate

__all__ = [
    "AckCreate",
    "AckResponse",
    "AsignacionCreate",
    "AvisoCreate",
    "AvisoListResponse",
    "AvisoResponse",
    "AvisoStatsResponse",
    "AvisoUpdate",
    "AsignacionMasivaRequest",
    "AsignacionResponse",
    "AsignacionUpdate",
    "CloneEquipoRequest",
    "ColumnaDetectada",
    "EntradaPadronList",
    "EntradaPadronResponse",
    "EquipoDestino",
    "EquipoOrigen",
    "FilaPreview",
    "ImportConfirmRequest",
    "ImportConfirmResponse",
    "ImportPreviewResponse",
    "UsuarioCreate",
    "UsuarioResponse",
    "UsuarioUpdate",
    "VaciarResponse",
    "VersionPadronList",
    "VersionPadronResponse",
    "VigenciaUpdateRequest",
    "VigenciaUpdateResponse",
]