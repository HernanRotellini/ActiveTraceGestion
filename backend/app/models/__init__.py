"""Modelos ORM del backend."""

from app.models.audit_log import AuditLog
from app.models.aviso import AcknowledgmentAviso, AlcanceAviso, Aviso, SeveridadAviso
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
from app.models.liquidaciones import (
    EstadoFactura,
    EstadoLiquidacion,
    Factura,
    Liquidacion,
    MateriaPlus,
    RolLiquidacion,
    SalarioBase,
    SalarioPlus,
)
from app.models.programas import FechaAcademica, ProgramaMateria, TipoFechaAcademica
from app.models.tarea import ComentarioTarea, EstadoTarea, Tarea
from app.models.usuarios_asignaciones import Asignacion, Usuario
from app.models.hilo_mensaje import HiloMensaje
from app.models.mensaje_interno import MensajeInterno
from app.models.rbac import Permiso, Rol, RolPermiso
from app.models.padron import EntradaPadron, VersionPadron
from app.models.tenant import Tenant

__all__ = [
    "AcknowledgmentAviso",
    "AlcanceAviso",
    "Asignacion",
    "AuditLog",
    "Aviso",
    "AuthUser",
    "BaseModelMixin",
    "Calificacion",
    "Carrera",
    "Cohorte",
    "Comunicacion",
    "ComentarioTarea",
    "ConvocatoriaAlumno",
    "EntradaPadron",
    "EstadoComunicacion",
    "EstadoEvaluacion",
    "EstadoFactura",
    "EstadoLiquidacion",
    "EstadoReserva",
    "EstadoTarea",
    "Evaluacion",
    "Factura",
    "FechaAcademica",
    "HiloMensaje",
    "Liquidacion",
    "Materia",
    "MateriaPlus",
    "MensajeInterno",
    "OrigenCalificacion",
    "PasswordRecoveryToken",
    "Permiso",
    "ProgramaMateria",
    "RefreshSession",
    "ResultadoEvaluacion",
    "ReservaEvaluacion",
    "Rol",
    "RolLiquidacion",
    "SeveridadAviso",
    "RolPermiso",
    "SalarioBase",
    "SalarioPlus",
    "SoftDeleteMixin",
    "Tenant",
    "Tarea",
    "TipoFechaAcademica",
    "TipoEvaluacion",
    "TurnoEvaluacion",
    "TenantScopedMixin",
    "TotpFactor",
    "TwoFactorChallenge",
    "UmbralMateria",
    "Usuario",
    "VersionPadron",
]
