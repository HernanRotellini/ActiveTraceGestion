"""Servicio de orquestación para el módulo de avisos institucionales.

Cubre operaciones CRUD, visualización filtrada por perfil,
confirmación de lectura (acknowledgment) y estadísticas.
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import Aviso
from app.repositories.acknowledgment_repository import AcknowledgmentRepository
from app.repositories.aviso_repository import AvisoRepository

logger = logging.getLogger(__name__)


class AvisoError(ValueError):
    """Error base del módulo de avisos."""


class AvisoNotFoundError(AvisoError):
    """Aviso no encontrado."""


class AvisoService:
    """Orquesta operaciones del tablón de avisos."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._aviso_repo = AvisoRepository(session, tenant_id)
        self._ack_repo = AcknowledgmentRepository(session, tenant_id)

    async def listar_visibles(
        self,
        roles: list[str],
        materia_ids: list[UUID] | None = None,
        cohorte_ids: list[UUID] | None = None,
    ) -> list[Aviso]:
        """Lista avisos visibles para un usuario."""
        return await self._aviso_repo.listar_visibles(roles, materia_ids, cohorte_ids)

    async def listar_admin(
        self,
        alcance: str | None = None,
        severidad: str | None = None,
        activo: bool | None = None,
    ) -> list[Aviso]:
        """Lista todos los avisos del tenant (para gestión)."""
        return await self._aviso_repo.listar_admin(alcance, severidad, activo)

    async def obtener_por_id(self, aviso_id: UUID) -> Aviso | None:
        """Obtiene un aviso por ID con scope de tenant."""
        return await self._aviso_repo.get(aviso_id)

    async def crear(self, datos: dict, actor_id: UUID) -> Aviso:
        """Crea un nuevo aviso y registra auditoría."""
        aviso = Aviso(
            tenant_id=self.tenant_id,
            alcance=datos["alcance"],
            materia_id=datos.get("materia_id"),
            cohorte_id=datos.get("cohorte_id"),
            rol_destino=datos.get("rol_destino"),
            severidad=datos.get("severidad", "Info"),
            titulo=datos["titulo"],
            cuerpo=datos["cuerpo"],
            inicio_en=datos["inicio_en"],
            fin_en=datos.get("fin_en"),
            orden=datos.get("orden", 0),
            activo=datos.get("activo", True),
            requiere_ack=datos.get("requiere_ack", False),
        )
        result = await self._aviso_repo.crear(aviso)
        await self._registrar_auditoria(actor_id, "AVISO_CREAR", str(result.id), {
            "alcance": datos["alcance"],
            "titulo": datos["titulo"],
        })
        return result

    async def actualizar(self, aviso_id: UUID, datos: dict, actor_id: UUID) -> Aviso:
        """Actualiza un aviso existente y registra auditoría."""
        aviso = await self._aviso_repo.get(aviso_id)
        if aviso is None:
            raise AvisoNotFoundError(f"Aviso {aviso_id} not found")

        result = await self._aviso_repo.actualizar(aviso_id, datos)
        if result is None:
            raise AvisoNotFoundError(f"Aviso {aviso_id} not found")

        await self._registrar_auditoria(actor_id, "AVISO_MODIFICAR", str(aviso_id), {
            "campos_modificados": list(datos.keys()),
        })
        return result

    async def desactivar(self, aviso_id: UUID, actor_id: UUID) -> None:
        """Desactiva un aviso (soft delete) y registra auditoría."""
        ok = await self._aviso_repo.desactivar(aviso_id)
        if not ok:
            raise AvisoNotFoundError(f"Aviso {aviso_id} not found")

        await self._registrar_auditoria(actor_id, "AVISO_DESACTIVAR", str(aviso_id), {})

    async def confirmar_lectura(self, aviso_id: UUID, usuario_id: UUID) -> None:
        """Confirma lectura de un aviso. Idempotente."""
        await self._ack_repo.confirmar(aviso_id, usuario_id)

    async def listar_pendientes_ack(
        self,
        usuario_id: UUID,
        roles: list[str],
        materia_ids: list[UUID] | None = None,
        cohorte_ids: list[UUID] | None = None,
    ) -> list[Aviso]:
        """Lista avisos visibles con requiere_ack=true que el usuario no ha confirmado."""
        return await self._ack_repo.listar_avisos_pendientes_ack(
            usuario_id, roles, materia_ids, cohorte_ids,
        )

    async def obtener_stats(self, aviso_id: UUID) -> dict:
        """Obtiene estadísticas de confirmación de un aviso."""
        stats = await self._aviso_repo.obtener_stats(aviso_id)
        return stats

    # ── Auditoría ────────────────────────────────────────────────

    async def _registrar_auditoria(
        self, actor_id: UUID, accion: str, recurso_id: str, detalle: dict,
    ) -> None:
        """Registra acción en audit log si el módulo está disponible."""
        try:
            from app.models.audit import AuditLog  # noqa: PLC0415

            entry = AuditLog(
                tenant_id=self.tenant_id,
                actor_id=actor_id,
                accion=accion,
                recurso_id=recurso_id,
                recurso_tipo="aviso",
                detalle=detalle,
            )
            self.session.add(entry)
        except (ImportError, Exception):
            # C-05 audit log no disponible o error al grabar
            pass
