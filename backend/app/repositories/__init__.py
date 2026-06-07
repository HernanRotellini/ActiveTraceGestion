"""Repositories del backend."""

from app.repositories.acknowledgment_repository import AcknowledgmentRepository
from app.repositories.aviso_repository import AvisoRepository
from app.repositories.asignaciones import AsignacionRepository
from app.repositories.base import TenantContextRequiredError, TenantScopedRepository
from app.repositories.calificaciones import CalificacionRepository, UmbralMateriaRepository
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.repositories.padron import EntradaPadronRepository, VersionPadronRepository
from app.repositories.programa_repository import ProgramaMateriaRepository
from app.repositories.tenant import TenantRepository
from app.repositories.usuarios import UsuarioRepository

__all__ = [
    "AcknowledgmentRepository",
    "AsignacionRepository",
    "AvisoRepository",
    "CalificacionRepository",
    "EntradaPadronRepository",
    "FechaAcademicaRepository",
    "TenantContextRequiredError",
    "TenantRepository",
    "TenantScopedRepository",
    "UmbralMateriaRepository",
    "ProgramaMateriaRepository",
    "UsuarioRepository",
    "VersionPadronRepository",
]
