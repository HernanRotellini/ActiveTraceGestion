"""Modelos ORM del backend."""

from app.models.base import BaseModelMixin, SoftDeleteMixin, TenantScopedMixin
from app.models.auth import AuthUser, PasswordRecoveryToken, RefreshSession, TotpFactor, TwoFactorChallenge
from app.models.estructura_academica import Carrera, Cohorte, Materia
from app.models.usuarios_asignaciones import Asignacion, Usuario
from app.models.rbac import Permiso, Rol, RolPermiso
from app.models.tenant import Tenant

__all__ = [
    "Asignacion",
    "AuthUser",
    "BaseModelMixin",
    "Carrera",
    "Cohorte",
    "Materia",
    "PasswordRecoveryToken",
    "Permiso",
    "RefreshSession",
    "Rol",
    "RolPermiso",
    "SoftDeleteMixin",
    "Tenant",
    "TenantScopedMixin",
    "TotpFactor",
    "TwoFactorChallenge",
    "Usuario",
]
