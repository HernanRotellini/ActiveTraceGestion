"""Servicio de mensajería interna (inbox)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.inbox_repository import InboxRepository
from app.repositories.usuarios import UsuarioRepository


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class NotParticipantError(ValueError):
    """Raised when user is not a participant in the thread."""


class InboxService:
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = InboxRepository(session, tenant_id)
        self._user_repo = UsuarioRepository(session, tenant_id, encryption_key)

    async def list_threads(self, usuario_id: UUID) -> list:
        hilos = await self._repo.list_by_participant(usuario_id)
        result = []
        for hilo in hilos:
            mensajes = await self._repo.get_mensajes_for_hilo(hilo.id)
            ultimo_mensaje = mensajes[-1].cuerpo if mensajes else None
            result.append({
                "id": hilo.id,
                "asunto": hilo.asunto,
                "participantes_ids": hilo.participantes_ids,
                "ultimo_mensaje_at": hilo.ultimo_mensaje_at,
                "created_at": hilo.created_at,
                "updated_at": hilo.updated_at,
                "ultimo_mensaje": ultimo_mensaje,
            })
        return result

    async def get_thread(self, hilo_id: UUID, usuario_id: UUID) -> dict | None:
        if not await self._repo.es_participante(hilo_id, usuario_id):
            return None
        hilo = await self._repo.get_with_mensajes(hilo_id)
        if hilo is None:
            return None
        mensajes = sorted(
            [m for m in (hilo.mensajes or [])],
            key=lambda m: m.created_at,
        )
        return {
            "id": hilo.id,
            "asunto": hilo.asunto,
            "participantes_ids": hilo.participantes_ids,
            "ultimo_mensaje_at": hilo.ultimo_mensaje_at,
            "created_at": hilo.created_at,
            "updated_at": hilo.updated_at,
            "mensajes": mensajes,
        }

    async def create_thread(self, remitente_id: UUID, asunto: str, destinatarios: list[UUID], cuerpo: str) -> dict:
        for dest_id in destinatarios:
            user = await self._user_repo.get(dest_id)
            if user is None:
                raise NotFoundError(f"User '{dest_id}' not found")

        participantes = list({remitente_id, *destinatarios})
        hilo = await self._repo.create_hilo(
            asunto=asunto,
            participantes_ids=participantes,
        )
        msg = await self._repo.create_mensaje(
            hilo_id=hilo.id,
            remitente_id=remitente_id,
            cuerpo=cuerpo,
        )
        return {
            "id": hilo.id,
            "asunto": hilo.asunto,
            "participantes_ids": hilo.participantes_ids,
            "ultimo_mensaje_at": hilo.ultimo_mensaje_at,
            "created_at": hilo.created_at,
            "updated_at": hilo.updated_at,
            "mensajes": [msg],
        }

    async def reply_to_thread(self, hilo_id: UUID, remitente_id: UUID, cuerpo: str) -> dict | None:
        if not await self._repo.es_participante(hilo_id, remitente_id):
            return None
        hilo = await self._repo.get(hilo_id)
        if hilo is None:
            return None
        msg = await self._repo.create_mensaje(
            hilo_id=hilo_id,
            remitente_id=remitente_id,
            cuerpo=cuerpo,
        )
        return {
            "id": msg.id,
            "hilo_id": msg.hilo_id,
            "remitente_id": msg.remitente_id,
            "cuerpo": msg.cuerpo,
            "created_at": msg.created_at,
        }
