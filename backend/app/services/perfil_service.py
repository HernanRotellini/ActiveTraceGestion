"""Servicio de perfil propio del usuario autenticado."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.repositories.usuarios import UsuarioRepository


class DuplicateEmailError(ValueError):
    """Raised when email already exists in the same tenant."""


class PerfilService:
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = UsuarioRepository(session, tenant_id, encryption_key)

    async def get_perfil(self, usuario_id: UUID):
        return await self._repo.get(usuario_id)

    async def update_perfil(self, usuario_id: UUID, **kwargs):
        record = await self._repo.get(usuario_id)
        if record is None:
            return None
        if "email" in kwargs and kwargs["email"] is not None and kwargs["email"] != record.email:
            existing = await self._repo.get_by_email(kwargs["email"])
            if existing is not None and existing.id != usuario_id:
                raise DuplicateEmailError(f"Email '{kwargs['email']}' already exists in this tenant")
        return await self._repo.update(usuario_id, **kwargs)
