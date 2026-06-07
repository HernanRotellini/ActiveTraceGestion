"""Servicio de tareas internas y workflow de estado."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import ComentarioTarea, EstadoTarea, Tarea
from app.repositories.tarea_repository import ComentarioTareaRepository, TareaRepository


class TareaError(ValueError):
    """Error base del módulo de tareas internas."""


class TareaNotFoundError(TareaError):
    """Tarea no encontrada en el tenant actual."""


class TareaValidationError(TareaError):
    """Datos inválidos para una operación de tarea."""


class TareaInvalidTransitionError(TareaError):
    """Transición de estado no permitida."""


class TareaService:
    """Orquesta tareas internas sin acceder directamente a la DB."""

    _allowed_transitions = {
        EstadoTarea.PENDIENTE: {EstadoTarea.EN_PROGRESO, EstadoTarea.CANCELADA},
        EstadoTarea.EN_PROGRESO: {EstadoTarea.RESUELTA, EstadoTarea.CANCELADA},
        EstadoTarea.RESUELTA: set(),
        EstadoTarea.CANCELADA: set(),
    }

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._tarea_repo = TareaRepository(session, tenant_id)
        self._comentario_repo = ComentarioTareaRepository(session, tenant_id)

    async def create_task(
        self,
        *,
        actor_id: UUID,
        titulo: str,
        descripcion: str,
        asignado_a: UUID,
        materia_id: UUID | None = None,
        contexto_id: UUID | None = None,
    ) -> Tarea:
        await self._validate_active_user(actor_id)
        await self._validate_active_user(asignado_a)
        if materia_id is not None:
            await self._validate_materia(materia_id)
        tarea = await self._tarea_repo.create(
            titulo=titulo,
            descripcion=descripcion,
            asignado_a=asignado_a,
            asignado_por=actor_id,
            materia_id=materia_id,
            contexto_id=contexto_id,
        )
        await self._registrar_auditoria(actor_id, "TAREA_CREAR", str(tarea.id), {"titulo": titulo})
        return tarea

    async def list_my(self, usuario_id: UUID, *, limit: int = 100, offset: int = 0) -> list[Tarea]:
        return await self._tarea_repo.list_my(usuario_id, limit=limit, offset=offset)

    async def list_global(
        self,
        *,
        asignado_a: UUID | None = None,
        asignado_por: UUID | None = None,
        materia_id: UUID | None = None,
        estado: EstadoTarea | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Tarea]:
        return await self._tarea_repo.list_global(
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            materia_id=materia_id,
            estado=estado,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_detail(self, tarea_id: UUID) -> Tarea:
        tarea = await self._tarea_repo.get(tarea_id)
        if tarea is None:
            raise TareaNotFoundError(f"Tarea {tarea_id} not found")
        tarea.comentarios = await self._comentario_repo.list_for_task(tarea_id)  # type: ignore[attr-defined]
        return tarea

    async def delegate_task(self, tarea_id: UUID, *, actor_id: UUID, asignado_a: UUID) -> Tarea:
        await self._validate_active_user(actor_id)
        await self._validate_active_user(asignado_a)
        tarea = await self._tarea_repo.update_assignment(
            tarea_id, asignado_a=asignado_a, asignado_por=actor_id
        )
        if tarea is None:
            raise TareaNotFoundError(f"Tarea {tarea_id} not found")
        await self._registrar_auditoria(actor_id, "TAREA_DELEGAR", str(tarea_id), {"asignado_a": str(asignado_a)})
        return tarea

    async def change_status(self, tarea_id: UUID, estado: EstadoTarea, *, actor_id: UUID | None = None) -> Tarea:
        tarea = await self._tarea_repo.get(tarea_id)
        if tarea is None:
            raise TareaNotFoundError(f"Tarea {tarea_id} not found")
        if estado not in self._allowed_transitions[tarea.estado]:
            raise TareaInvalidTransitionError(f"No se puede cambiar de {tarea.estado.value} a {estado.value}")
        updated = await self._tarea_repo.update_status(tarea_id, estado)
        if updated is None:
            raise TareaNotFoundError(f"Tarea {tarea_id} not found")
        if actor_id is not None:
            await self._registrar_auditoria(actor_id, "TAREA_CAMBIAR_ESTADO", str(tarea_id), {"estado": estado.value})
        return updated

    async def add_comment(self, tarea_id: UUID, *, autor_id: UUID, texto: str) -> ComentarioTarea:
        await self._validate_active_user(autor_id)
        tarea = await self._tarea_repo.get(tarea_id)
        if tarea is None:
            raise TareaNotFoundError(f"Tarea {tarea_id} not found")
        return await self._comentario_repo.create(tarea_id=tarea_id, autor_id=autor_id, texto=texto)

    async def _validate_active_user(self, usuario_id: UUID) -> None:
        if not await self._tarea_repo.user_is_active(usuario_id):
            raise TareaValidationError(f"Usuario {usuario_id} inválido para el tenant")

    async def _validate_materia(self, materia_id: UUID) -> None:
        if not await self._tarea_repo.materia_exists(materia_id):
            raise TareaValidationError(f"Materia {materia_id} inválida para el tenant")

    async def _registrar_auditoria(self, actor_id: UUID, accion: str, recurso_id: str, detalle: dict) -> None:
        try:
            from app.models.audit import AuditLog  # noqa: PLC0415

            self.session.add(
                AuditLog(
                    tenant_id=self.tenant_id,
                    actor_id=actor_id,
                    accion=accion,
                    recurso_id=recurso_id,
                    recurso_tipo="tarea",
                    detalle=detalle,
                )
            )
        except (ImportError, Exception):
            pass
