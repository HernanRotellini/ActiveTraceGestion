"""Servicio de Usuario con reglas de PII y unicidad de email."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.usuarios import UsuarioRepository


class DuplicateEmailError(ValueError):
    """Raised when email already exists in the same tenant."""


class NotFoundError(ValueError):
    """Raised when a referenced entity is not found."""


class UsuarioService:
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        self.session = session
        self.tenant_id = tenant_id
        self._repo = UsuarioRepository(session, tenant_id, encryption_key)

    async def create_usuario(self, **kwargs):
        email = kwargs.get("email", "")
        existing = await self._repo.get_by_email(email)
        if existing is not None:
            raise DuplicateEmailError(f"Email '{email}' already exists in this tenant")
        return await self._repo.create(**kwargs)

    async def get_usuario(self, usuario_id: UUID):
        return await self._repo.get(usuario_id)

    async def list_usuarios(self):
        return await self._repo.list()

    async def update_usuario(self, usuario_id: UUID, **kwargs):
        record = await self._repo.get(usuario_id)
        if record is None:
            raise NotFoundError(f"Usuario with id '{usuario_id}' not found")
        if "email" in kwargs and kwargs["email"] is not None and kwargs["email"] != record.email:
            existing = await self._repo.get_by_email(kwargs["email"])
            if existing is not None and existing.id != usuario_id:
                raise DuplicateEmailError(f"Email '{kwargs['email']}' already exists in this tenant")
        return await self._repo.update(usuario_id, **kwargs)

    async def delete_usuario(self, usuario_id: UUID) -> bool:
        return await self._repo.soft_delete(usuario_id)
