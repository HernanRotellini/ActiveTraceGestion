"""Modelos ORM del backend."""

from app.models.base import BaseModelMixin, SoftDeleteMixin, TenantScopedMixin
from app.models.auth import AuthUser, PasswordRecoveryToken, RefreshSession, TotpFactor, TwoFactorChallenge
from app.models.calificaciones import Calificacion, OrigenCalificacion, UmbralMateria
from app.models.coloquio import (
    ConvocatoriaAlumno,
    EstadoEvaluacion,
    EstadoReserva,
    Evaluacion,
    ResultadoEvaluacion,
    ReservaEvaluacion,
    TipoEvaluacion,
    TurnoEvaluacion,
)
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.estructura_academica import Carrera, Cohorte, Materia
from app.models.usuarios_asignaciones import Asignacion, Usuario
from app.models.rbac import Permiso, Rol, RolPermiso
from app.models.padron import EntradaPadron, VersionPadron
from app.models.tenant import Tenant

__all__ = [
    "Asignacion",
    "AuthUser",
    "BaseModelMixin",
    "Calificacion",
    "Carrera",
    "Cohorte",
    "Comunicacion",
    "ConvocatoriaAlumno",
    "EntradaPadron",
    "EstadoComunicacion",
    "EstadoEvaluacion",
    "EstadoReserva",
    "Evaluacion",
    "Materia",
    "OrigenCalificacion",
    "PasswordRecoveryToken",
    "Permiso",
    "RefreshSession",
    "ResultadoEvaluacion",
    "ReservaEvaluacion",
    "Rol",
    "RolPermiso",
    "SoftDeleteMixin",
    "Tenant",
    "TipoEvaluacion",
    "TurnoEvaluacion",
    "TenantScopedMixin",
    "TotpFactor",
    "TwoFactorChallenge",
    "UmbralMateria",
    "Usuario",
    "VersionPadron",
]
