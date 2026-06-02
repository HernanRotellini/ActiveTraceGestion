"""Repositories tenant-scoped de autenticación."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import AuthUser, PasswordRecoveryToken, RefreshSession, TotpFactor, TwoFactorChallenge
from app.repositories.base import TenantScopedRepository


class AuthUserRepository(TenantScopedRepository[AuthUser]):
    """Acceso a usuarios de auth siempre filtrado por tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, AuthUser, tenant_id)

    async def get_by_email(self, email: str) -> AuthUser | None:
        """Busca usuario activo/no eliminado por email normalizado dentro del tenant."""
        result = await self.session.execute(
            select(AuthUser).where(
                AuthUser.tenant_id == self.tenant_id,
                AuthUser.deleted_at.is_(None),
                func.lower(AuthUser.email) == email.lower(),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, user_id: UUID) -> AuthUser | None:
        return await self.get(user_id)


class RefreshSessionRepository(TenantScopedRepository[RefreshSession]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, RefreshSession, tenant_id)

    async def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshSession:
        refresh = RefreshSession(tenant_id=self.tenant_id, user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(refresh)
        await self.session.flush()
        return refresh

    async def revoke_by_hash(self, token_hash: str) -> RefreshSession | None:
        refresh = await self.get_by_hash(token_hash)
        if refresh is not None and refresh.revoked_at is None:
            refresh.revoked_at = datetime.now(UTC)
        return refresh

    async def get_by_hash(self, token_hash: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(
                RefreshSession.tenant_id == self.tenant_id,
                RefreshSession.deleted_at.is_(None),
                RefreshSession.token_hash == token_hash,
            )
        )
        return result.scalar_one_or_none()

    async def find_by_hash(self, token_hash: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(RefreshSession.deleted_at.is_(None), RefreshSession.token_hash == token_hash)
        )
        return result.scalar_one_or_none()


class TotpFactorRepository(TenantScopedRepository[TotpFactor]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, TotpFactor, tenant_id)

    async def get_by_user_id(self, user_id: UUID) -> TotpFactor | None:
        result = await self.session.execute(
            select(TotpFactor).where(
                TotpFactor.tenant_id == self.tenant_id,
                TotpFactor.user_id == user_id,
                TotpFactor.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()


class TwoFactorChallengeRepository(TenantScopedRepository[TwoFactorChallenge]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, TwoFactorChallenge, tenant_id)

    async def get_active(self, challenge_id: UUID) -> TwoFactorChallenge | None:
        result = await self.session.execute(
            select(TwoFactorChallenge).where(
                TwoFactorChallenge.tenant_id == self.tenant_id,
                TwoFactorChallenge.id == challenge_id,
                TwoFactorChallenge.used_at.is_(None),
                TwoFactorChallenge.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()


class PasswordRecoveryRepository(TenantScopedRepository[PasswordRecoveryToken]):
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        super().__init__(session, PasswordRecoveryToken, tenant_id)

    async def find_by_hash(self, token_hash: str) -> PasswordRecoveryToken | None:
        result = await self.session.execute(
            select(PasswordRecoveryToken).where(
                PasswordRecoveryToken.deleted_at.is_(None),
                PasswordRecoveryToken.token_hash == token_hash,
            )
        )
        return result.scalar_one_or_none()


class AuthTokenLookupRepository:
    """Lookups por verificador opaco antes de conocer tenant por sesión."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_refresh_by_hash(self, token_hash: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(RefreshSession.deleted_at.is_(None), RefreshSession.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def find_recovery_by_hash(self, token_hash: str) -> PasswordRecoveryToken | None:
        result = await self.session.execute(
            select(PasswordRecoveryToken).where(
                PasswordRecoveryToken.deleted_at.is_(None), PasswordRecoveryToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def find_challenge_by_id(self, challenge_id: UUID) -> TwoFactorChallenge | None:
        result = await self.session.execute(
            select(TwoFactorChallenge).where(
                TwoFactorChallenge.id == challenge_id,
                TwoFactorChallenge.deleted_at.is_(None),
                TwoFactorChallenge.used_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
