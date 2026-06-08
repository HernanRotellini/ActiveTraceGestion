"""Servicios de autenticación."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.encryption import decrypt_sensitive_value, encrypt_sensitive_value
from app.core.security import (
    TokenError,
    create_access_token,
    generate_opaque_token,
    generate_totp_secret,
    hash_password,
    hash_token,
    totp_code,
    verify_access_token,
    verify_password,
    verify_totp,
)
from app.models.auth import AuthUser, PasswordRecoveryToken, RefreshSession, TotpFactor, TwoFactorChallenge
from app.repositories.auth import (
    AuthTokenLookupRepository,
    AuthUserRepository,
    PasswordRecoveryRepository,
    RefreshSessionRepository,
    TotpFactorRepository,
    TwoFactorChallengeRepository,
)
from app.repositories.tenant import TenantRepository


class AuthenticationError(ValueError):
    """Credenciales o token inválido."""


class InactiveUserError(ValueError):
    """Usuario inactivo."""


class RateLimitExceededError(ValueError):
    """Límite de intentos excedido."""


@dataclass(frozen=True)
class CurrentUser:
    user_id: UUID
    tenant_id: UUID
    roles: list[str]
    impersonator_id: UUID | None = None


@dataclass(frozen=True)
class LoginResult:
    access_token: str | None = None
    refresh_token: str | None = None
    challenge_id: UUID | None = None

    @property
    def requires_2fa(self) -> bool:
        return self.challenge_id is not None


class LoginRateLimiter:
    """Rate limiter reemplazable por IP+email."""

    def __init__(self, *, limit: int = 5, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._attempts: dict[tuple[str, str], list[datetime]] = {}

    def check(self, ip_address: str, email: str) -> None:
        now = datetime.now(UTC)
        key = (ip_address, email.lower())
        window_start = now - timedelta(seconds=self.window_seconds)
        attempts = [attempt for attempt in self._attempts.get(key, []) if attempt > window_start]
        if len(attempts) >= self.limit:
            self._attempts[key] = attempts
            raise RateLimitExceededError("too many login attempts")
        attempts.append(now)
        self._attempts[key] = attempts

    def reset_all(self) -> None:
        self._attempts.clear()


login_rate_limiter = LoginRateLimiter()


class AuthService:
    """Orquesta auth vía repositories; no consulta DB directamente."""

    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or Settings()  # type: ignore[call-arg]

    async def login(self, *, tenant_code: str, email: str, password: str, ip_address: str) -> LoginResult:
        login_rate_limiter.check(ip_address, email)
        tenant = await TenantRepository(self.session).get_active_by_code(tenant_code)
        if tenant is None:
            raise AuthenticationError("invalid credentials")
        user_repo = AuthUserRepository(self.session, tenant.id)
        user = await user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("invalid credentials")
        if not user.is_active:
            raise InactiveUserError("inactive user")
        factor = await TotpFactorRepository(self.session, tenant.id).get_by_user_id(user.id)
        if factor is not None and factor.enabled_at is not None:
            challenge = TwoFactorChallenge(
                tenant_id=tenant.id,
                user_id=user.id,
                expires_at=datetime.now(UTC) + timedelta(minutes=5),
            )
            self.session.add(challenge)
            await self.session.commit()
            return LoginResult(challenge_id=challenge.id)
        return await self._issue_session(user)

    async def refresh(self, refresh_token: str) -> LoginResult:
        token_hash = hash_token(refresh_token)
        refresh = await AuthTokenLookupRepository(self.session).find_refresh_by_hash(token_hash)
        if not self._refresh_is_usable(refresh):
            raise AuthenticationError("invalid refresh token")
        assert refresh is not None
        user = await AuthUserRepository(self.session, refresh.tenant_id).get_active_by_id(refresh.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("invalid refresh token")
        refresh.revoked_at = datetime.now(UTC)
        result = await self._issue_session(user)
        new_hash = hash_token(result.refresh_token or "")
        new_refresh = await RefreshSessionRepository(self.session, user.tenant_id).get_by_hash(new_hash)
        refresh.rotated_to_id = new_refresh.id if new_refresh is not None else None
        await self.session.commit()
        return result

    async def logout(self, refresh_token: str, current_user: CurrentUser) -> None:
        repo = RefreshSessionRepository(self.session, current_user.tenant_id)
        await repo.revoke_by_hash(hash_token(refresh_token))
        await self.session.commit()

    async def current_user_from_token(self, token: str) -> CurrentUser:
        try:
            claims = verify_access_token(token, self.settings)
            tenant_id = UUID(claims["tenant_id"])
            user_id = UUID(claims["user_id"])
        except (TokenError, ValueError) as exc:
            raise AuthenticationError("invalid access token") from exc
        user = await AuthUserRepository(self.session, tenant_id).get_active_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("invalid access token")
        return CurrentUser(user_id=user.id, tenant_id=user.tenant_id, roles=list(user.roles))

    async def enroll_totp(self, current_user: CurrentUser) -> tuple[str, str]:
        secret = generate_totp_secret()
        repo = TotpFactorRepository(self.session, current_user.tenant_id)
        factor = await repo.get_by_user_id(current_user.user_id)
        encrypted = encrypt_sensitive_value(secret, encryption_key=self.settings.ENCRYPTION_KEY)
        if factor is None:
            self.session.add(TotpFactor(tenant_id=current_user.tenant_id, user_id=current_user.user_id, encrypted_secret=encrypted))
        else:
            factor.encrypted_secret = encrypted
            factor.enabled_at = None
        await self.session.commit()
        return secret, totp_code(secret)

    async def verify_totp_enrollment(self, current_user: CurrentUser, code: str) -> None:
        factor = await TotpFactorRepository(self.session, current_user.tenant_id).get_by_user_id(current_user.user_id)
        if factor is None or not self._verify_factor(factor, code):
            raise AuthenticationError("invalid totp")
        factor.enabled_at = datetime.now(UTC)
        await self.session.commit()

    async def complete_totp_challenge(self, challenge_id: UUID, code: str) -> LoginResult:
        challenge = await self._find_challenge(challenge_id)
        if challenge is None or challenge.expires_at <= datetime.now(UTC):
            raise AuthenticationError("invalid challenge")
        factor = await TotpFactorRepository(self.session, challenge.tenant_id).get_by_user_id(challenge.user_id)
        if factor is None or factor.enabled_at is None or not self._verify_factor(factor, code):
            raise AuthenticationError("invalid challenge")
        user = await AuthUserRepository(self.session, challenge.tenant_id).get_active_by_id(challenge.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("invalid challenge")
        challenge.used_at = datetime.now(UTC)
        result = await self._issue_session(user)
        await self.session.commit()
        return result

    async def forgot_password(self, *, tenant_code: str, email: str) -> str | None:
        tenant = await TenantRepository(self.session).get_active_by_code(tenant_code)
        if tenant is None:
            return None
        user = await AuthUserRepository(self.session, tenant.id).get_by_email(email)
        if user is None or not user.is_active:
            return None
        token = generate_opaque_token()
        self.session.add(
            PasswordRecoveryToken(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=datetime.now(UTC) + timedelta(minutes=30),
            )
        )
        await self.session.commit()
        return token

    async def reset_password(self, *, token: str, new_password: str) -> None:
        recovery = await AuthTokenLookupRepository(self.session).find_recovery_by_hash(hash_token(token))
        if recovery is None or recovery.used_at is not None or recovery.expires_at <= datetime.now(UTC):
            raise AuthenticationError("invalid recovery token")
        user = await AuthUserRepository(self.session, recovery.tenant_id).get_active_by_id(recovery.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("invalid recovery token")
        user.password_hash = hash_password(new_password)
        recovery.used_at = datetime.now(UTC)
        await self.session.commit()

    async def _issue_session(self, user: AuthUser) -> LoginResult:
        refresh_token = generate_opaque_token()
        await RefreshSessionRepository(self.session, user.tenant_id).create(
            user.id, hash_token(refresh_token), datetime.now(UTC) + timedelta(days=30)
        )
        access_token = create_access_token(user_id=user.id, tenant_id=user.tenant_id, roles=list(user.roles), settings=self.settings)
        await self.session.commit()
        return LoginResult(access_token=access_token, refresh_token=refresh_token)

    def _verify_factor(self, factor: TotpFactor, code: str) -> bool:
        secret = decrypt_sensitive_value(factor.encrypted_secret, encryption_key=self.settings.ENCRYPTION_KEY)
        return verify_totp(secret, code)

    async def _find_challenge(self, challenge_id: UUID) -> TwoFactorChallenge | None:
        return await AuthTokenLookupRepository(self.session).find_challenge_by_id(challenge_id)

    @staticmethod
    def _refresh_is_usable(refresh: RefreshSession | None) -> bool:
        return refresh is not None and refresh.revoked_at is None and refresh.expires_at > datetime.now(UTC)
