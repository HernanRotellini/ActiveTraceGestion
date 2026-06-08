"""Repository tenant-scoped para mensajería interna."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.hilo_mensaje import HiloMensaje
from app.models.mensaje_interno import MensajeInterno
from app.repositories.base import TenantScopedRepository


class InboxRepository(TenantScopedRepository[HiloMensaje]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, HiloMensaje, tenant_id)

    async def list_by_participant(self, usuario_id: UUID) -> list[HiloMensaje]:
        result = await self.session.execute(
            select(HiloMensaje).where(
                HiloMensaje.tenant_id == self.tenant_id,
                HiloMensaje.deleted_at.is_(None),
                HiloMensaje.participantes_ids.contains([str(usuario_id)]),
            ).order_by(HiloMensaje.ultimo_mensaje_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def get_with_mensajes(self, hilo_id: UUID) -> HiloMensaje | None:
        result = await self.session.execute(
            select(HiloMensaje)
            .where(
                HiloMensaje.id == hilo_id,
                HiloMensaje.tenant_id == self.tenant_id,
                HiloMensaje.deleted_at.is_(None),
            )
            .options(selectinload(HiloMensaje.mensajes))
        )
        return result.scalar_one_or_none()

    async def create_hilo(self, asunto: str, participantes_ids: list[UUID]) -> HiloMensaje:
        hilo = HiloMensaje(
            tenant_id=self.tenant_id,
            asunto=asunto,
            participantes_ids=[str(pid) for pid in participantes_ids],
            ultimo_mensaje_at=None,
        )
        self.session.add(hilo)
        await self.session.flush()
        return hilo

    async def create_mensaje(self, hilo_id: UUID, remitente_id: UUID, cuerpo: str) -> MensajeInterno:
        msg = MensajeInterno(
            hilo_id=hilo_id,
            remitente_id=remitente_id,
            cuerpo=cuerpo,
        )
        self.session.add(msg)
        await self.session.flush()

        hilo = await self.get(hilo_id)
        if hilo is not None:
            from datetime import UTC, datetime
            hilo.ultimo_mensaje_at = datetime.now(UTC)

        return msg

    async def get_mensajes_for_hilo(self, hilo_id: UUID) -> list[MensajeInterno]:
        result = await self.session.execute(
            select(MensajeInterno)
            .where(MensajeInterno.hilo_id == hilo_id)
            .order_by(MensajeInterno.created_at.asc())
        )
        return list(result.scalars().all())

    async def es_participante(self, hilo_id: UUID, usuario_id: UUID) -> bool:
        hilo = await self.get(hilo_id)
        if hilo is None:
            return False
        return str(usuario_id) in hilo.participantes_ids
