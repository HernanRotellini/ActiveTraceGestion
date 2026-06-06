"""Repositorio tenant-scoped para el modelo AcknowledgmentAviso.

Operaciones de confirmación de lectura con semántica
idempotente y consultas de pendientes.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.aviso import AcknowledgmentAviso, Aviso


class AcknowledgmentRepository:
    """Acceso a datos de acknowledgments, siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self.session = session
        self.tenant_id = tenant_id

    async def confirmar(self, aviso_id: UUID, usuario_id: UUID) -> AcknowledgmentAviso:
        """Crea un acknowledgment. Idempotente: si ya existe, retorna el existente."""
        now = datetime.now(UTC)

        # Intentar insert con ON CONFLICT DO NOTHING
        stmt = (
            pg_insert(AcknowledgmentAviso)
            .values(
                tenant_id=self.tenant_id,
                aviso_id=aviso_id,
                usuario_id=usuario_id,
                confirmado_at=now,
            )
            .on_conflict_do_nothing(
                constraint="uq_aviso_usuario_ack",
            )
        )
        await self.session.execute(stmt)
        await self.session.flush()

        # Retornar el registro (existente o recién creado)
        result = await self.session.execute(
            select(AcknowledgmentAviso).where(
                AcknowledgmentAviso.aviso_id == aviso_id,
                AcknowledgmentAviso.usuario_id == usuario_id,
                AcknowledgmentAviso.tenant_id == self.tenant_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def obtener_por_aviso_y_usuario(
        self, aviso_id: UUID, usuario_id: UUID,
    ) -> AcknowledgmentAviso | None:
        """Verifica si un usuario ya confirmó un aviso."""
        result = await self.session.execute(
            select(AcknowledgmentAviso).where(
                AcknowledgmentAviso.aviso_id == aviso_id,
                AcknowledgmentAviso.usuario_id == usuario_id,
                AcknowledgmentAviso.tenant_id == self.tenant_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def contar_por_aviso(self, aviso_id: UUID) -> int:
        """Cantidad de confirmaciones para un aviso."""
        result = await self.session.execute(
            select(func.count()).where(
                AcknowledgmentAviso.aviso_id == aviso_id,
                AcknowledgmentAviso.tenant_id == self.tenant_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    async def listar_usuarios_sin_confirmar(
        self, aviso_id: UUID,
    ) -> list[UUID]:
        """Lista usuarios que aún no confirmaron este aviso."""
        # Esta función requiere conocer los destinatarios potenciales.
        # Por ahora retorna lista vacía; se implementa cuando se integre
        # con el módulo de usuarios/asignaciones.
        _ = aviso_id
        return []

    async def listar_ids_avisos_confirmados(
        self, usuario_id: UUID,
    ) -> list[UUID]:
        """Lista IDs de avisos que el usuario ya confirmó."""
        result = await self.session.execute(
            select(AcknowledgmentAviso.aviso_id).where(
                AcknowledgmentAviso.usuario_id == usuario_id,
                AcknowledgmentAviso.tenant_id == self.tenant_id,
                AcknowledgmentAviso.deleted_at.is_(None),
            )
        )
        return [row[0] for row in result.all()]

    async def listar_avisos_pendientes_ack(
        self,
        usuario_id: UUID,
        roles: list[str],
        materia_ids: list[UUID] | None = None,
        cohorte_ids: list[UUID] | None = None,
    ) -> list[Aviso]:
        """Lista avisos visibles con requiere_ack=true que el usuario no ha confirmado."""
        from app.models.aviso import Aviso

        now = datetime.now(UTC)
        confirmed_ids = await self.listar_ids_avisos_confirmados(usuario_id)

        stmt = (
            select(Aviso)
            .where(
                Aviso.tenant_id == self.tenant_id,
                Aviso.activo.is_(True),
                Aviso.deleted_at.is_(None),
                Aviso.requiere_ack.is_(True),
                Aviso.inicio_en <= now,
            )
            .where(
                (Aviso.fin_en.is_(None)) | (Aviso.fin_en >= now),
            )
        )

        # Excluir ya confirmados
        if confirmed_ids:
            stmt = stmt.where(Aviso.id.notin_(confirmed_ids))

        # Filtros de alcance (misma lógica que AvisoRepository.listar_visibles)
        from sqlalchemy import or_

        conditions = [Aviso.alcance == "Global"]
        if roles:
            conditions.append(
                (Aviso.alcance == "PorRol") & Aviso.rol_destino.in_(roles)
            )
        if materia_ids:
            conditions.append(
                (Aviso.alcance == "PorMateria") & Aviso.materia_id.in_(materia_ids)
            )
        if cohorte_ids:
            conditions.append(
                (Aviso.alcance == "PorCohorte") & Aviso.cohorte_id.in_(cohorte_ids)
            )

        stmt = stmt.where(or_(*conditions))
        stmt = stmt.order_by(Aviso.orden.asc(), Aviso.inicio_en.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
