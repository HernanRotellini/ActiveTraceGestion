"""Tests para C-16 Tareas internas.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base


@pytest.fixture
async def tareas_schema(db_engine: None):
    """Creates a fresh schema for tareas internas tests."""
    from app.models.auth import AuthUser  # noqa: F401
    from app.models.estructura_academica import Materia  # noqa: F401
    from app.models.rbac import Permiso, Rol, RolPermiso  # noqa: F401
    from app.models.tarea import ComentarioTarea, Tarea  # noqa: F401
    from app.models.tenant import Tenant  # noqa: F401
    from app.models.usuarios_asignaciones import Usuario  # noqa: F401

    from app.core.database import get_sessionmaker

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        connection = await session.connection()
        await connection.execute(text("DROP SCHEMA public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.run_sync(Base.metadata.create_all)
        await session.commit()


@pytest.fixture
async def tenant_id(db_session: AsyncSession, tareas_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Tenant C16", code=f"c16-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
async def otro_tenant_id(db_session: AsyncSession, tareas_schema: None) -> UUID:
    from app.models.tenant import Tenant

    tenant = Tenant(id=uuid4(), name="Otro Tenant C16", code=f"c16-other-{uuid4().hex[:8]}")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


async def crear_usuario(db_session: AsyncSession, tenant_id: UUID, **overrides: Any) -> UUID:
    from app.models.usuarios_asignaciones import Usuario

    defaults = {
        "tenant_id": tenant_id,
        "nombre": "Ada",
        "apellidos": "Lovelace",
        "email": f"{uuid4()}@example.com",
        "estado": "activo",
    }
    defaults.update(overrides)
    usuario = Usuario(**defaults)
    db_session.add(usuario)
    await db_session.flush()
    return usuario.id


async def crear_materia(db_session: AsyncSession, tenant_id: UUID, **overrides: Any) -> UUID:
    from app.models.estructura_academica import Materia

    defaults = {
        "tenant_id": tenant_id,
        "codigo": f"MAT-{uuid4().hex[:6]}",
        "nombre": "Materia C16",
        "estado": "activa",
    }
    defaults.update(overrides)
    materia = Materia(**defaults)
    db_session.add(materia)
    await db_session.flush()
    return materia.id


async def crear_tarea(
    db_session: AsyncSession,
    tenant_id: UUID,
    asignado_a: UUID,
    asignado_por: UUID,
    **overrides: Any,
) -> UUID:
    from app.models.tarea import EstadoTarea, Tarea

    defaults = {
        "tenant_id": tenant_id,
        "titulo": "Revisar seguimiento",
        "descripcion": "Contactar docente responsable",
        "estado": EstadoTarea.PENDIENTE,
        "asignado_a": asignado_a,
        "asignado_por": asignado_por,
    }
    defaults.update(overrides)
    tarea = Tarea(**defaults)
    db_session.add(tarea)
    await db_session.flush()
    return tarea.id


class TestTareaModel:
    async def test_crear_tarea_pendiente_con_tenant_y_asignacion(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.tarea import EstadoTarea, Tarea

        asignador_id = await crear_usuario(db_session, tenant_id, email="asignador@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="asignado@example.com")
        materia_id = await crear_materia(db_session, tenant_id)

        tarea_id = await crear_tarea(
            db_session,
            tenant_id,
            asignado_a=asignado_id,
            asignado_por=asignador_id,
            materia_id=materia_id,
            contexto_id=uuid4(),
        )

        result = await db_session.execute(select(Tarea).where(Tarea.id == tarea_id))
        tarea = result.scalar_one()

        assert tarea.tenant_id == tenant_id
        assert tarea.estado == EstadoTarea.PENDIENTE
        assert tarea.asignado_a == asignado_id
        assert tarea.asignado_por == asignador_id
        assert tarea.materia_id == materia_id
        assert tarea.deleted_at is None

    async def test_comentario_tarea_guarda_autor_y_texto(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.tarea import ComentarioTarea

        autor_id = await crear_usuario(db_session, tenant_id, email="autor@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="asignado2@example.com")
        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=autor_id)

        comentario = ComentarioTarea(
            tenant_id=tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto="Queda delegado para seguimiento.",
        )
        db_session.add(comentario)
        await db_session.flush()

        result = await db_session.execute(
            select(ComentarioTarea).where(ComentarioTarea.tarea_id == tarea_id)
        )
        saved = result.scalar_one()
        assert saved.tenant_id == tenant_id
        assert saved.autor_id == autor_id
        assert saved.texto == "Queda delegado para seguimiento."
        assert saved.deleted_at is None

    async def test_soft_delete_excluye_tarea_desde_repository_base(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.base import TenantScopedRepository
        from app.models.tarea import Tarea

        asignador_id = await crear_usuario(db_session, tenant_id, email="asignador3@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="asignado3@example.com")
        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=asignador_id)

        repo = TenantScopedRepository(db_session, Tarea, tenant_id)
        assert await repo.get(tarea_id) is not None

        assert await repo.soft_delete(tarea_id) is True
        await db_session.flush()

        assert await repo.get(tarea_id) is None

    async def test_metadata_define_indices_de_alto_uso(
        self, db_session: AsyncSession, tareas_schema: None
    ) -> None:
        connection = await db_session.connection()
        indexes = await connection.run_sync(
            lambda sync_conn: inspect(sync_conn).get_indexes("tarea")
        )
        index_names = {index["name"] for index in indexes}

        assert "ix_tarea_tenant_asignado_estado" in index_names
        assert "ix_tarea_tenant_asignador" in index_names
        assert "ix_tarea_tenant_materia" in index_names
        assert "ix_tarea_tenant_estado" in index_names
        assert "ix_tarea_tenant_updated_at" in index_names


class TestTareaRepository:
    async def test_create_get_and_list_my_are_tenant_scoped(
        self,
        db_session: AsyncSession,
        tareas_schema: None,
        tenant_id: UUID,
        otro_tenant_id: UUID,
    ) -> None:
        from app.models.tarea import EstadoTarea
        from app.repositories.tarea_repository import TareaRepository

        actor_id = await crear_usuario(db_session, tenant_id, email="actor@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="mine@example.com")
        otro_actor_id = await crear_usuario(db_session, otro_tenant_id, email="otro-actor@example.com")
        otro_asignado_id = await crear_usuario(db_session, otro_tenant_id, email="otro-mine@example.com")

        repo = TareaRepository(db_session, tenant_id)
        tarea = await repo.create(
            titulo="Llamar docente",
            descripcion="Resolver atraso de entrega",
            asignado_a=asignado_id,
            asignado_por=actor_id,
        )
        await crear_tarea(
            db_session,
            otro_tenant_id,
            asignado_a=otro_asignado_id,
            asignado_por=otro_actor_id,
            titulo="No visible",
        )

        assert tarea.estado == EstadoTarea.PENDIENTE
        assert await repo.get(tarea.id) is not None
        assert await repo.get(uuid4()) is None

        mine = await repo.list_my(asignado_id)
        assert [item.id for item in mine] == [tarea.id]

    async def test_list_global_filters_and_search(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.tarea import EstadoTarea
        from app.repositories.tarea_repository import TareaRepository

        actor_id = await crear_usuario(db_session, tenant_id, email="actor2@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="asignado4@example.com")
        otro_id = await crear_usuario(db_session, tenant_id, email="otro4@example.com")
        materia_id = await crear_materia(db_session, tenant_id, codigo="MAT-FILTRO")
        await crear_tarea(
            db_session,
            tenant_id,
            asignado_a=asignado_id,
            asignado_por=actor_id,
            materia_id=materia_id,
            estado=EstadoTarea.EN_PROGRESO,
            titulo="Seguimiento Moodle",
            descripcion="Buscar entregas pendientes",
        )
        await crear_tarea(
            db_session,
            tenant_id,
            asignado_a=otro_id,
            asignado_por=actor_id,
            estado=EstadoTarea.PENDIENTE,
            titulo="Otra tarea",
        )

        repo = TareaRepository(db_session, tenant_id)
        filtered = await repo.list_global(
            asignado_a=asignado_id,
            asignado_por=actor_id,
            materia_id=materia_id,
            estado=EstadoTarea.EN_PROGRESO,
            search="moodle",
        )

        assert len(filtered) == 1
        assert filtered[0].titulo == "Seguimiento Moodle"

    async def test_delegate_and_comments_are_tenant_scoped(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.repositories.tarea_repository import ComentarioTareaRepository, TareaRepository

        actor_id = await crear_usuario(db_session, tenant_id, email="actor3@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="asignado5@example.com")
        nuevo_id = await crear_usuario(db_session, tenant_id, email="nuevo5@example.com")

        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=actor_id)
        repo = TareaRepository(db_session, tenant_id)
        updated = await repo.update_assignment(tarea_id, asignado_a=nuevo_id, asignado_por=actor_id)

        assert updated is not None
        assert updated.asignado_a == nuevo_id
        assert updated.asignado_por == actor_id

        comments = ComentarioTareaRepository(db_session, tenant_id)
        await comments.create(tarea_id=tarea_id, autor_id=actor_id, texto="Delegado a coordinación")
        await comments.create(tarea_id=tarea_id, autor_id=nuevo_id, texto="Tomado")

        thread = await comments.list_for_task(tarea_id)
        assert [comment.texto for comment in thread] == ["Delegado a coordinación", "Tomado"]


class TestTareaService:
    async def test_create_uses_session_actor_and_validates_same_tenant(
        self,
        db_session: AsyncSession,
        tareas_schema: None,
        tenant_id: UUID,
        otro_tenant_id: UUID,
    ) -> None:
        from app.services.tarea_service import TareaService, TareaValidationError

        actor_id = await crear_usuario(db_session, tenant_id, email="svc-actor@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="svc-asignado@example.com")
        materia_id = await crear_materia(db_session, tenant_id)
        cross_user_id = await crear_usuario(db_session, otro_tenant_id, email="svc-cross@example.com")

        service = TareaService(db_session, tenant_id)
        tarea = await service.create_task(
            actor_id=actor_id,
            titulo="Coordinar seguimiento",
            descripcion="Hablar con docente",
            asignado_a=asignado_id,
            materia_id=materia_id,
        )

        assert tarea.asignado_por == actor_id
        assert tarea.asignado_a == asignado_id

        with pytest.raises(TareaValidationError):
            await service.create_task(
                actor_id=actor_id,
                titulo="Cross tenant",
                descripcion="No debe crearse",
                asignado_a=cross_user_id,
            )

    async def test_delegate_rejects_inactive_user_without_mutating_assignment(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.tarea_service import TareaService, TareaValidationError

        actor_id = await crear_usuario(db_session, tenant_id, email="svc-actor2@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="svc-asignado2@example.com")
        inactive_id = await crear_usuario(
            db_session, tenant_id, email="svc-inactive@example.com", estado="inactivo"
        )
        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=actor_id)

        service = TareaService(db_session, tenant_id)
        with pytest.raises(TareaValidationError):
            await service.delegate_task(tarea_id, actor_id=actor_id, asignado_a=inactive_id)

        unchanged = await service.get_detail(tarea_id)
        assert unchanged.asignado_a == asignado_id

    async def test_status_transitions_and_terminal_rejection(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.models.tarea import EstadoTarea
        from app.services.tarea_service import TareaInvalidTransitionError, TareaService

        actor_id = await crear_usuario(db_session, tenant_id, email="svc-actor3@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="svc-asignado3@example.com")
        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=actor_id)

        service = TareaService(db_session, tenant_id)
        in_progress = await service.change_status(tarea_id, EstadoTarea.EN_PROGRESO)
        assert in_progress.estado == EstadoTarea.EN_PROGRESO

        resolved = await service.change_status(tarea_id, EstadoTarea.RESUELTA)

        assert resolved.estado == EstadoTarea.RESUELTA
        with pytest.raises(TareaInvalidTransitionError):
            await service.change_status(tarea_id, EstadoTarea.PENDIENTE)

    async def test_add_comment_uses_session_author_and_returns_chronological_thread(
        self, db_session: AsyncSession, tareas_schema: None, tenant_id: UUID
    ) -> None:
        from app.services.tarea_service import TareaService

        actor_id = await crear_usuario(db_session, tenant_id, email="svc-actor4@example.com")
        asignado_id = await crear_usuario(db_session, tenant_id, email="svc-asignado4@example.com")
        tarea_id = await crear_tarea(db_session, tenant_id, asignado_a=asignado_id, asignado_por=actor_id)

        service = TareaService(db_session, tenant_id)
        first = await service.add_comment(tarea_id, autor_id=actor_id, texto="Primero")
        second = await service.add_comment(tarea_id, autor_id=asignado_id, texto="Segundo")

        assert first.autor_id == actor_id
        assert second.autor_id == asignado_id
        detail = await service.get_detail(tarea_id)
        assert [comment.texto for comment in detail.comentarios] == ["Primero", "Segundo"]
