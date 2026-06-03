"""Repository tenant-scoped para Usuario con cifrado PII transparente."""

import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from app.core.encryption import decrypt_sensitive_value, encrypt_sensitive_value
from app.models.usuarios_asignaciones import Usuario
from app.repositories.base import TenantScopedRepository

PII_FIELDS = {"email", "dni", "cuil", "cbu", "alias_cbu"}


def _email_hash(email: str) -> str:
    """Deterministic SHA-256 hash of email for duplicate lookups."""
    return hashlib.sha256(email.lower().encode("utf-8")).hexdigest()


def _encrypt_pii(obj: Usuario, encryption_key: str) -> None:
    for field in PII_FIELDS:
        value = getattr(obj, field, None)
        if value is not None:
            setattr(obj, field, encrypt_sensitive_value(value, encryption_key=encryption_key))


def _decrypt_pii(obj: Usuario, encryption_key: str) -> None:
    for field in PII_FIELDS:
        value = getattr(obj, field, None)
        if value is not None:
            try:
                setattr(obj, field, decrypt_sensitive_value(value, encryption_key=encryption_key))
            except Exception:
                pass


def _decrypt_pii_list(objs: list[Usuario], encryption_key: str) -> None:
    for obj in objs:
        _decrypt_pii(obj, encryption_key)


def _mark_pii_clean(obj: Usuario) -> None:
    """Mark PII fields as 'clean' so the next commit doesn't auto-flush
    the decrypted in-memory values over the encrypted DB values."""
    for field in PII_FIELDS:
        val = getattr(obj, field, None)
        if val is not None:
            set_committed_value(obj, field, val)


class UsuarioRepository(TenantScopedRepository[Usuario]):
    def __init__(self, session: AsyncSession, tenant_id: UUID, encryption_key: str) -> None:
        super().__init__(session, Usuario, tenant_id)
        self.encryption_key = encryption_key

    async def get_by_email(self, email: str) -> Usuario | None:
        hash_val = _email_hash(email)
        result = await self.session.execute(
            select(Usuario).where(
                Usuario.tenant_id == self.tenant_id,
                Usuario.deleted_at.is_(None),
                Usuario.email_hash == hash_val,
            )
        )
        record = result.scalar_one_or_none()
        if record is not None:
            _decrypt_pii(record, self.encryption_key)
        return record

    async def create(self, **kwargs) -> Usuario:
        record = Usuario(tenant_id=self.tenant_id, **kwargs)
        if record.email:
            record.email_hash = _email_hash(record.email)
        _encrypt_pii(record, self.encryption_key)
        self.session.add(record)
        await self.session.flush()
        _decrypt_pii(record, self.encryption_key)
        _mark_pii_clean(record)
        return record

    async def get(self, record_id: UUID) -> Usuario | None:
        record = await super().get(record_id)
        if record is not None:
            _decrypt_pii(record, self.encryption_key)
        return record

    async def list(self) -> list[Usuario]:
        records = await super().list()
        _decrypt_pii_list(records, self.encryption_key)
        return records

    async def update(self, record_id: UUID, **kwargs) -> Usuario | None:
        record = await super().get(record_id)
        if record is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(record, key, value)
        if "email" in kwargs and kwargs["email"] is not None:
            record.email_hash = _email_hash(kwargs["email"])
        _encrypt_pii(record, self.encryption_key)
        await self.session.flush()
        # Refresh to load server-generated values (updated_at)
        await self.session.refresh(record)
        _decrypt_pii(record, self.encryption_key)
        _mark_pii_clean(record)
        return record
