"""Repositorios tenant-scoped para tareas internas."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.estructura_academica import Materia
from app.models.tarea import ComentarioTarea, EstadoTarea, Tarea
from app.models.usuarios_asignaciones import Usuario
from app.repositories.base import TenantScopedRepository


class TareaRepository(TenantScopedRepository[Tarea]):
    """Acceso a datos de tareas, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, Tarea, tenant_id)

    async def create(
        self,
        *,
        titulo: str,
        descripcion: str,
        asignado_a: UUID,
        asignado_por: UUID,
        materia_id: UUID | None = None,
        contexto_id: UUID | None = None,
    ) -> Tarea:
        tarea = Tarea(
            tenant_id=self.tenant_id,
            titulo=titulo,
            descripcion=descripcion,
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            materia_id=materia_id,
            contexto_id=contexto_id,
        )
        self.session.add(tarea)
        await self.session.flush()
        return tarea

    async def list_my(self, usuario_id: UUID, *, limit: int = 100, offset: int = 0) -> list[Tarea]:
        result = await self.session.execute(
            select(Tarea)
            .where(
                Tarea.tenant_id == self.tenant_id,
                Tarea.asignado_a == usuario_id,
                Tarea.deleted_at.is_(None),
            )
            .order_by(Tarea.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

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
        stmt = select(Tarea).where(
            Tarea.tenant_id == self.tenant_id,
            Tarea.deleted_at.is_(None),
        )
        if asignado_a is not None:
            stmt = stmt.where(Tarea.asignado_a == asignado_a)
        if asignado_por is not None:
            stmt = stmt.where(Tarea.asignado_por == asignado_por)
        if materia_id is not None:
            stmt = stmt.where(Tarea.materia_id == materia_id)
        if estado is not None:
            stmt = stmt.where(Tarea.estado == estado)
        if search:
            term = f"%{search}%"
            stmt = stmt.where(or_(Tarea.titulo.ilike(term), Tarea.descripcion.ilike(term)))

        result = await self.session.execute(
            stmt.order_by(Tarea.updated_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def update_assignment(
        self, tarea_id: UUID, *, asignado_a: UUID, asignado_por: UUID
    ) -> Tarea | None:
        tarea = await self.get(tarea_id)
        if tarea is None:
            return None
        tarea.asignado_a = asignado_a
        tarea.asignado_por = asignado_por
        await self.session.flush()
        await self.session.refresh(tarea)
        return tarea

    async def update_status(self, tarea_id: UUID, estado: EstadoTarea) -> Tarea | None:
        tarea = await self.get(tarea_id)
        if tarea is None:
            return None
        tarea.estado = estado
        await self.session.flush()
        await self.session.refresh(tarea)
        return tarea

    async def user_is_active(self, usuario_id: UUID) -> bool:
        result = await self.session.execute(
            select(Usuario.id).where(
                Usuario.id == usuario_id,
                Usuario.tenant_id == self.tenant_id,
                Usuario.estado == "activo",
                Usuario.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none() is not None

    async def materia_exists(self, materia_id: UUID) -> bool:
        result = await self.session.execute(
            select(Materia.id).where(
                Materia.id == materia_id,
                Materia.tenant_id == self.tenant_id,
                Materia.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none() is not None


class ComentarioTareaRepository(TenantScopedRepository[ComentarioTarea]):
    """Acceso a comentarios de tareas, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, ComentarioTarea, tenant_id)

    async def create(self, *, tarea_id: UUID, autor_id: UUID, texto: str) -> ComentarioTarea:
        comentario = ComentarioTarea(
            tenant_id=self.tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
        )
        self.session.add(comentario)
        await self.session.flush()
        return comentario

    async def list_for_task(self, tarea_id: UUID) -> list[ComentarioTarea]:
        result = await self.session.execute(
            select(ComentarioTarea)
            .where(
                ComentarioTarea.tenant_id == self.tenant_id,
                ComentarioTarea.tarea_id == tarea_id,
                ComentarioTarea.deleted_at.is_(None),
            )
            .order_by(ComentarioTarea.created_at.asc())
        )
        return list(result.scalars().all())
