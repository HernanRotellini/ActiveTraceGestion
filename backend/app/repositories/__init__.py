"""Repositories del backend."""

from app.repositories.asignaciones import AsignacionRepository
from app.repositories.base import TenantContextRequiredError, TenantScopedRepository
from app.repositories.padron import EntradaPadronRepository, VersionPadronRepository
from app.repositories.tenant import TenantRepository
from app.repositories.usuarios import UsuarioRepository

__all__ = [
    "AsignacionRepository",
    "EntradaPadronRepository",
    "TenantContextRequiredError",
    "TenantRepository",
    "TenantScopedRepository",
    "UsuarioRepository",
    "VersionPadronRepository",
]
