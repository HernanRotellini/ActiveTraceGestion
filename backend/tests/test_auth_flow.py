"""Acceptance tests for C-03 authentication flows."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.security import hash_password, hash_token, verify_password, generate_opaque_token
from app.services.auth import login_rate_limiter
from app.models.auth import AuthUser, PasswordRecoveryToken, RefreshSession, TotpFactor, TwoFactorChallenge
from app.models.tenant import Tenant
from app.repositories.auth import (
    AuthUserRepository,
    RefreshSessionRepository,
    TotpFactorRepository,
    TwoFactorChallengeRepository,
    AuthTokenLookupRepository,
    PasswordRecoveryRepository,
)


@pytest.fixture
async def auth_flow_schema(db_engine: None):
    async with _metadata_context():
        yield


@pytest.fixture(autouse=True)
def reset_login_rate_limiter() -> None:
    login_rate_limiter.reset_all()


class _metadata_context:
    async def __aenter__(self) -> None:
        from app.core.database import get_sessionmaker

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(
                text(
                    "DROP TABLE IF EXISTS password_recovery_tokens, two_factor_challenges, "
                    "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
                )
            )
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)
            await session.commit()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        from app.core.database import get_sessionmaker

        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            connection = await session.connection()
            await connection.execute(
                text(
                    "DROP TABLE IF EXISTS password_recovery_tokens, two_factor_challenges, "
                    "totp_factors, refresh_sessions, auth_users, tenants CASCADE"
                )
            )
            await session.commit()


async def create_tenant(db_session: AsyncSession, code: str) -> Tenant:
    tenant = Tenant(name=f"Tenant {code}", code=code)
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def create_user(
    db_session: AsyncSession,
    tenant: Tenant,
    *,
    email: str = "user@example.com",
    password: str = "correct-password",
    is_active: bool = True,
    roles: list[str] | None = None,
) -> AuthUser:
    user = AuthUser(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        roles=roles or ["ALUMNO"],
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.flush()
    return user


async def login(
    client: AsyncClient,
    *,
    tenant_code: str,
    email: str = "user@example.com",
    password: str = "correct-password",
) -> dict:
    response = await client.post(
        "/api/auth/login",
        json={"tenant_code": tenant_code, "email": email, "password": password},
    )
    return response.json()


class TestLoginAndAccessJwt:
    async def test_login_uses_tenant_code_and_issues_tokens(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant, roles=["ADMIN", "TUTOR"])
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "USER@example.com", "password": "correct-password"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["token_type"] == "bearer"
        assert payload["access_token"]
        assert payload["refresh_token"]
        claims = jwt.get_unverified_claims(payload["access_token"])
        assert claims["sub"] == str(user.id)
        assert claims["user_id"] == str(user.id)
        assert claims["tenant_id"] == str(tenant.id)
        assert claims["roles"] == ["ADMIN", "TUTOR"]

    @pytest.mark.parametrize(
        ("password", "is_active", "expected_status"),
        [("wrong-password", True, 401), ("correct-password", False, 403)],
    )
    async def test_login_failures_do_not_issue_tokens(
        self,
        auth_flow_schema: None,
        db_session: AsyncSession,
        async_client: AsyncClient,
        password: str,
        is_active: bool,
        expected_status: int,
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant, is_active=is_active)
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "user@example.com", "password": password},
        )

        assert response.status_code == expected_status
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    async def test_access_jwt_contains_minimal_claims_without_permissions(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant, roles=["COORDINADOR"])
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        claims = jwt.get_unverified_claims(payload["access_token"])

        assert set(claims) >= {"sub", "user_id", "tenant_id", "roles", "exp"}
        assert "permissions" not in claims
        assert "effective_permissions" not in claims
        assert claims["exp"] - int(datetime.now(UTC).timestamp()) <= 15 * 60


class TestCurrentUserDependencyAndLogout:
    async def test_valid_token_resolves_user_context_and_ignores_request_identity(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")

        response = await async_client.get(
            f"/api/auth/me?tenant_id={uuid4()}&user_id={uuid4()}",
            headers={"Authorization": f"Bearer {payload['access_token']}", "X-Tenant-Id": str(uuid4())},
        )

        assert response.status_code == 200
        assert response.json() == {
            "user_id": str(user.id),
            "tenant_id": str(tenant.id),
            "roles": ["ALUMNO"],
        }

    @pytest.mark.parametrize("token", ["not-a-jwt", "ey.bad.signature"])
    async def test_invalid_access_tokens_fail_closed(
        self, auth_flow_schema: None, async_client: AsyncClient, token: str
    ) -> None:
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    async def test_expired_access_token_fails_closed(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()
        expired = jwt.encode(
            {
                "sub": str(user.id),
                "user_id": str(user.id),
                "tenant_id": str(tenant.id),
                "roles": user.roles,
                "exp": datetime.now(UTC) - timedelta(minutes=1),
            },
            "dev-secret-key-change-in-production!!",
            algorithm="HS256",
        )

        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired}"},
        )

        assert response.status_code == 401

    async def test_logout_revokes_refresh_token(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")

        logout_response = await async_client.post(
            "/api/auth/logout",
            json={"refresh_token": payload["refresh_token"]},
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )
        refresh_response = await async_client.post(
            "/api/auth/refresh", json={"refresh_token": payload["refresh_token"]}
        )

        assert logout_response.status_code == 204
        assert refresh_response.status_code == 401


class TestRefreshRotation:
    async def test_valid_refresh_rotates_token_and_preserves_context(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")

        response = await async_client.post(
            "/api/auth/refresh", json={"refresh_token": payload["refresh_token"]}
        )

        assert response.status_code == 200
        rotated = response.json()
        assert rotated["refresh_token"] != payload["refresh_token"]
        claims = jwt.get_unverified_claims(rotated["access_token"])
        assert claims["sub"] == str(user.id)
        assert claims["tenant_id"] == str(tenant.id)
        stored = (await db_session.execute(select(RefreshSession))).scalars().all()
        assert all(session.token_hash != payload["refresh_token"] for session in stored)

    async def test_reused_expired_or_revoked_refresh_tokens_fail_closed(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")
        first = await async_client.post("/api/auth/refresh", json={"refresh_token": payload["refresh_token"]})

        expired_token = "expired-refresh"
        db_session.add(
            RefreshSession(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(expired_token),
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            )
        )
        revoked_token = "revoked-refresh"
        db_session.add(
            RefreshSession(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(revoked_token),
                expires_at=datetime.now(UTC) + timedelta(days=1),
                revoked_at=datetime.now(UTC),
            )
        )
        await db_session.commit()

        reused = await async_client.post("/api/auth/refresh", json={"refresh_token": payload["refresh_token"]})
        expired = await async_client.post("/api/auth/refresh", json={"refresh_token": expired_token})
        revoked = await async_client.post("/api/auth/refresh", json={"refresh_token": revoked_token})

        assert first.status_code == 200
        assert reused.status_code == 401
        assert expired.status_code == 401
        assert revoked.status_code == 401
        assert "access_token" not in reused.json()


class TestTotpTwoFactor:
    async def test_totp_enrollment_requires_valid_code_to_enable(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}

        enrollment = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        invalid = await async_client.post(
            "/api/auth/2fa/verify", headers=headers, json={"code": "000000"}
        )
        valid = await async_client.post(
            "/api/auth/2fa/verify", headers=headers, json={"code": enrollment.json()["current_code"]}
        )

        assert enrollment.status_code == 200
        assert enrollment.json()["secret"]
        assert invalid.status_code == 401
        assert valid.status_code == 204
        factor = await db_session.scalar(select(TotpFactor).where(TotpFactor.user_id == user.id))
        assert factor is not None
        assert factor.enabled_at is not None
        assert factor.encrypted_secret != enrollment.json()["secret"]

    async def test_2fa_login_challenge_gates_session_until_valid_totp(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()
        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}
        enrollment = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        await async_client.post(
            "/api/auth/2fa/verify", headers=headers, json={"code": enrollment.json()["current_code"]}
        )

        challenge_response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "user@example.com", "password": "correct-password"},
        )
        challenge_id = challenge_response.json()["challenge_id"]
        invalid = await async_client.post(
            "/api/auth/2fa/challenge", json={"challenge_id": challenge_id, "code": "000000"}
        )
        valid = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": challenge_id, "code": enrollment.json()["current_code"]},
        )
        expired = await async_client.post(
            "/api/auth/2fa/challenge", json={"challenge_id": str(uuid4()), "code": enrollment.json()["current_code"]}
        )

        assert challenge_response.status_code == 200
        assert challenge_response.json()["requires_2fa"] is True
        assert "access_token" not in challenge_response.json()
        assert invalid.status_code == 401
        assert valid.status_code == 200
        assert valid.json()["access_token"]
        assert expired.status_code == 401


class TestPasswordRecovery:
     async def test_recovery_request_is_generic_and_creates_one_use_token_for_active_user(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()

        known = await async_client.post(
            "/api/auth/forgot", json={"tenant_code": "utn", "email": "user@example.com"}
        )
        unknown = await async_client.post(
            "/api/auth/forgot", json={"tenant_code": "utn", "email": "missing@example.com"}
        )

        assert known.status_code == 202
        assert unknown.status_code == 202
        # Same message for both known and unknown accounts (no enumeration)
        assert known.json()["message"] == unknown.json()["message"]
        # No recovery_token in response (should be None)
        assert known.json()["recovery_token"] is None
        assert unknown.json()["recovery_token"] is None
        # But a token SHOULD exist in the database for the known user
        token = await db_session.scalar(select(PasswordRecoveryToken))
        assert token is not None

     async def test_password_reset_accepts_valid_token_once_and_rejects_used_or_expired(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        # Verify forgot endpoint returns generic response for known and unknown accounts
        known = await async_client.post(
            "/api/auth/forgot", json={"tenant_code": "utn", "email": "user@example.com"}
        )
        unknown = await async_client.post(
            "/api/auth/forgot", json={"tenant_code": "utn", "email": "missing@example.com"}
        )
        assert known.status_code == 202
        assert unknown.status_code == 202
        assert known.json()["recovery_token"] is None
        assert unknown.json()["recovery_token"] is None
        
        # Generate a token directly for testing reset endpoint
        valid_token = generate_opaque_token()
        db_session.add(
            PasswordRecoveryToken(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(valid_token),
                expires_at=datetime.now(UTC) + timedelta(minutes=30),
            )
        )
        
        # Generate an expired token for testing rejection
        expired_token = "expired-recovery"
        db_session.add(
            PasswordRecoveryToken(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(expired_token),
                expires_at=datetime.now(UTC) - timedelta(seconds=1),
            )
        )
        await db_session.commit()

        # First use of valid token should succeed
        valid = await async_client.post(
            "/api/auth/reset", json={"token": valid_token, "new_password": "new-password"}
        )
        # Reuse of valid token should fail
        reused = await async_client.post(
            "/api/auth/reset", json={"token": valid_token, "new_password": "another-password"}
        )
        # Expired token should fail
        expired = await async_client.post(
            "/api/auth/reset", json={"token": expired_token, "new_password": "new-password"}
        )
        await db_session.refresh(user)

        assert valid.status_code == 204
        assert verify_password("new-password", user.password_hash) is True
        assert reused.status_code == 401
        assert expired.status_code == 401


class TestLoginRateLimiting:
    async def test_login_rate_limit_blocks_sixth_attempt_and_resets_window(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()

        statuses = []
        for _ in range(6):
            response = await async_client.post(
                "/api/auth/login",
                json={"tenant_code": "utn", "email": "user@example.com", "password": "wrong"},
            )
            statuses.append(response.status_code)
        login_rate_limiter.reset_all()
        after_reset = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "user@example.com", "password": "wrong"},
        )

        assert statuses[:5] == [401, 401, 401, 401, 401]
        assert statuses[5] == 429
        assert after_reset.status_code == 401


class TestAuthServiceEdgeCases:
    """Edge cases and error paths in AuthService."""

    async def test_login_with_nonexistent_tenant_returns_auth_error(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """LOGIN: invalid tenant code should return generic 401."""
        response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "nonexistent", "email": "user@example.com", "password": "password"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    async def test_login_with_empty_email_fails_validation(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """LOGIN: empty email should be rejected by Pydantic before reaching service."""
        tenant = await create_tenant(db_session, "utn")
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "", "password": "password"},
        )

        # Pydantic validation should reject empty email
        assert response.status_code == 422

    async def test_login_with_very_long_email_fails_validation(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """LOGIN: email longer than schema max should fail validation."""
        tenant = await create_tenant(db_session, "utn")
        await db_session.commit()

        long_email = "a" * 500 + "@example.com"
        response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": long_email, "password": "password"},
        )

        assert response.status_code == 422

    async def test_refresh_with_invalid_refresh_token_format_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """REFRESH: malformed refresh token should return 401."""
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": "not-a-valid-opaque-token!!!"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"

    async def test_refresh_with_empty_token_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """REFRESH: empty token should fail with validation error."""
        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": ""},
        )

        assert response.status_code == 422

    async def test_refresh_when_user_becomes_inactive_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """REFRESH: if user becomes inactive after login, refresh should fail."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        refresh_token = payload["refresh_token"]

        # Deactivate the user
        user.is_active = False
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401

    async def test_totp_enrollment_replaces_existing_factor(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """TOTP: enrolling twice should replace the previous factor."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}

        # First enrollment
        first = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        first_secret = first.json()["secret"]

        # Second enrollment without verifying first
        second = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        second_secret = second.json()["secret"]

        # Secrets should differ
        assert first_secret != second_secret

        # Factor should be updated (not duplicated)
        factors = (await db_session.execute(select(TotpFactor).where(TotpFactor.user_id == user.id))).scalars().all()
        assert len(factors) == 1

    async def test_totp_enrollment_with_empty_code_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """TOTP VERIFY: empty code should be rejected by Pydantic."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}

        await async_client.post("/api/auth/2fa/enroll", headers=headers)

        response = await async_client.post(
            "/api/auth/2fa/verify",
            headers=headers,
            json={"code": ""},
        )

        assert response.status_code == 422

    async def test_totp_challenge_with_invalid_uuid_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """2FA CHALLENGE: invalid UUID format should be caught."""
        response = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": "not-a-uuid", "code": "123456"},
        )

        assert response.status_code == 401

    async def test_totp_challenge_with_expired_challenge_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """2FA CHALLENGE: expired challenge should be rejected."""
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}

        # Enroll and verify TOTP
        enrollment = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        await async_client.post(
            "/api/auth/2fa/verify", headers=headers, json={"code": enrollment.json()["current_code"]}
        )

        # Login to get a 2FA challenge
        challenge_response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "user@example.com", "password": "correct-password"},
        )
        challenge_id = challenge_response.json()["challenge_id"]

        # Manually expire the challenge in DB
        challenge = await db_session.scalar(
            select(TwoFactorChallenge).where(TwoFactorChallenge.id == UUID(challenge_id))
        )
        challenge.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": challenge_id, "code": enrollment.json()["current_code"]},
        )

        assert response.status_code == 401

    async def test_totp_challenge_on_already_used_challenge_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """2FA CHALLENGE: using an already-used challenge should fail."""
        tenant = await create_tenant(db_session, "utn")
        await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        headers = {"Authorization": f"Bearer {payload['access_token']}"}

        enrollment = await async_client.post("/api/auth/2fa/enroll", headers=headers)
        await async_client.post(
            "/api/auth/2fa/verify", headers=headers, json={"code": enrollment.json()["current_code"]}
        )

        challenge_response = await async_client.post(
            "/api/auth/login",
            json={"tenant_code": "utn", "email": "user@example.com", "password": "correct-password"},
        )
        challenge_id = challenge_response.json()["challenge_id"]

        # First use should succeed
        first = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": challenge_id, "code": enrollment.json()["current_code"]},
        )
        assert first.status_code == 200

        # Second use should fail (challenge already used)
        second = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": challenge_id, "code": enrollment.json()["current_code"]},
        )
        assert second.status_code == 401

    async def test_totp_challenge_without_enabled_factor_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """2FA CHALLENGE: if TOTP factor not enabled, challenge should fail."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        # Manually create a challenge (bypass normal login flow)
        challenge = TwoFactorChallenge(
            tenant_id=tenant.id,
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )
        db_session.add(challenge)
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/2fa/challenge",
            json={"challenge_id": str(challenge.id), "code": "123456"},
        )

        assert response.status_code == 401

    async def test_forgot_password_for_inactive_user_returns_generic_response(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """FORGOT PASSWORD: inactive users should get generic response (no enumeration)."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant, is_active=False)
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/forgot",
            json={"tenant_code": "utn", "email": "user@example.com"},
        )

        assert response.status_code == 202
        assert response.json()["message"] == "If the account exists, recovery instructions were sent"
        # Verify no token was created for inactive user
        tokens = (await db_session.execute(select(PasswordRecoveryToken))).scalars().all()
        assert len(tokens) == 0

    async def test_forgot_password_for_nonexistent_tenant_returns_generic_response(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """FORGOT PASSWORD: nonexistent tenant should return generic response."""
        response = await async_client.post(
            "/api/auth/forgot",
            json={"tenant_code": "nonexistent", "email": "user@example.com"},
        )

        assert response.status_code == 202
        assert response.json()["message"] == "If the account exists, recovery instructions were sent"

    async def test_reset_password_with_invalid_token_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """RESET PASSWORD: invalid token should fail closed."""
        response = await async_client.post(
            "/api/auth/reset",
            json={"token": "invalid-token", "new_password": "new-password"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid recovery token"

    async def test_reset_password_when_user_is_deleted_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """RESET PASSWORD: if user is soft-deleted, reset should fail."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        # Create a valid recovery token
        token = generate_opaque_token()
        db_session.add(
            PasswordRecoveryToken(
                tenant_id=tenant.id,
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=datetime.now(UTC) + timedelta(minutes=30),
            )
        )
        await db_session.commit()

        # Soft delete the user
        user.deleted_at = datetime.now(UTC)
        await db_session.commit()

        response = await async_client.post(
            "/api/auth/reset",
            json={"token": token, "new_password": "new-password"},
        )

        assert response.status_code == 401

    async def test_me_without_authorization_header_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """ME: missing Authorization header should return 401."""
        response = await async_client.get("/api/auth/me")

        assert response.status_code == 401

    async def test_me_with_malformed_bearer_token_fails(
        self, auth_flow_schema: None, async_client: AsyncClient
    ) -> None:
        """ME: malformed Bearer format should fail."""
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token"},
        )

        assert response.status_code == 401

    async def test_current_user_from_token_with_deleted_user_fails(
        self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
    ) -> None:
        """CURRENT USER: if user is soft-deleted, token should become invalid."""
        tenant = await create_tenant(db_session, "utn")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        payload = await login(async_client, tenant_code="utn")
        token = payload["access_token"]

        # Soft delete the user
        user.deleted_at = datetime.now(UTC)
        await db_session.commit()

        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    async def test_logout_without_valid_auth_still_succeeds(
         self, auth_flow_schema: None, db_session: AsyncSession, async_client: AsyncClient
     ) -> None:
         """LOGOUT: should require authentication to logout."""
         tenant = await create_tenant(db_session, "utn")
         await create_user(db_session, tenant)
         await db_session.commit()

         # Try logout without authentication
         response = await async_client.post(
             "/api/auth/logout",
             json={"refresh_token": "some-token"},
         )

         # Should fail due to missing auth
         assert response.status_code == 401


class TestAuthRepositoryEdgeCases:
    """Edge cases in AuthRepository queries."""

    async def test_get_by_email_normalizes_case(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET BY EMAIL: email lookup should be case-insensitive."""
        tenant = await create_tenant(db_session, "repo-a")
        user = await create_user(db_session, tenant, email="TestUser@Example.COM")
        await db_session.commit()

        repo = AuthUserRepository(db_session, tenant.id)

        # All variations should find the same user
        result1 = await repo.get_by_email("testuser@example.com")
        result2 = await repo.get_by_email("TESTUSER@EXAMPLE.COM")
        result3 = await repo.get_by_email("TestUser@Example.COM")

        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        assert result1.id == user.id
        assert result2.id == user.id
        assert result3.id == user.id

    async def test_get_by_email_returns_none_for_missing_user(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET BY EMAIL: missing email should return None."""
        tenant = await create_tenant(db_session, "repo-b")
        await db_session.commit()

        repo = AuthUserRepository(db_session, tenant.id)
        result = await repo.get_by_email("missing@example.com")

        assert result is None

    async def test_get_active_by_id_is_tenant_scoped(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET ACTIVE BY ID: should not cross tenant boundaries."""
        tenant_a = await create_tenant(db_session, "repo-c-a")
        tenant_b = await create_tenant(db_session, "repo-c-b")
        user_a = await create_user(db_session, tenant_a)
        await db_session.commit()

        repo_b = AuthUserRepository(db_session, tenant_b.id)
        result = await repo_b.get_active_by_id(user_a.id)

        # Should not find user from other tenant
        assert result is None

    async def test_refresh_session_find_by_hash_crosses_tenants(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """FIND BY HASH (refresh): should find token across tenants (before tenant is known)."""
        tenant_a = await create_tenant(db_session, "repo-d-a")
        tenant_b = await create_tenant(db_session, "repo-d-b")
        user_a = await create_user(db_session, tenant_a)
        user_b = await create_user(db_session, tenant_b)
        await db_session.commit()

        # Create refresh sessions in different tenants
        repo_a = RefreshSessionRepository(db_session, tenant_a.id)
        repo_b = RefreshSessionRepository(db_session, tenant_b.id)

        token_a = "token-a-12345"
        session_a = await repo_a.create(user_a.id, hash_token(token_a), datetime.now(UTC) + timedelta(days=30))

        # Now look it up with the cross-tenant lookup
        lookup = AuthTokenLookupRepository(db_session)
        found = await lookup.find_refresh_by_hash(hash_token(token_a))

        assert found is not None
        assert found.user_id == user_a.id
        assert found.tenant_id == tenant_a.id

    async def test_refresh_get_by_hash_is_tenant_scoped(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET BY HASH (refresh, tenant-scoped): should only find within tenant."""
        tenant_a = await create_tenant(db_session, "repo-e-a")
        tenant_b = await create_tenant(db_session, "repo-e-b")
        user_a = await create_user(db_session, tenant_a)
        user_b = await create_user(db_session, tenant_b)
        await db_session.commit()

        repo_a = RefreshSessionRepository(db_session, tenant_a.id)
        repo_b = RefreshSessionRepository(db_session, tenant_b.id)

        token_a = "token-a-scoped-12345"
        await repo_a.create(user_a.id, hash_token(token_a), datetime.now(UTC) + timedelta(days=30))

        # Try to find it from tenant_b's repo (should fail)
        result = await repo_b.get_by_hash(hash_token(token_a))

        assert result is None

    async def test_totp_factor_get_by_user_id_is_tenant_scoped(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET BY USER ID (TOTP): should be tenant-scoped."""
        tenant_a = await create_tenant(db_session, "repo-f-a")
        tenant_b = await create_tenant(db_session, "repo-f-b")
        user_a = await create_user(db_session, tenant_a)
        user_b = await create_user(db_session, tenant_b)
        await db_session.commit()

        repo_a = TotpFactorRepository(db_session, tenant_a.id)
        repo_b = TotpFactorRepository(db_session, tenant_b.id)

        factor_a = TotpFactor(tenant_id=tenant_a.id, user_id=user_a.id, encrypted_secret="secret-a")
        db_session.add(factor_a)
        await db_session.flush()

        # Try to find from tenant_b (should fail)
        result = await repo_b.get_by_user_id(user_a.id)

        assert result is None

    async def test_two_factor_challenge_get_active_excludes_used_challenges(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """GET ACTIVE (challenge): should exclude already-used challenges."""
        tenant = await create_tenant(db_session, "repo-g")
        user = await create_user(db_session, tenant)
        await db_session.commit()

        repo = TwoFactorChallengeRepository(db_session, tenant.id)

        # Create a used challenge
        used = TwoFactorChallenge(
            tenant_id=tenant.id,
            user_id=user.id,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            used_at=datetime.now(UTC),
        )
        db_session.add(used)
        await db_session.flush()

        # Try to get it (should fail because it's used)
        result = await repo.get_active(used.id)

        assert result is None

    async def test_password_recovery_find_by_hash_is_tenant_agnostic(
        self, auth_flow_schema: None, db_session: AsyncSession
    ) -> None:
        """FIND BY HASH (recovery): should find token across tenants (before tenant known)."""
        tenant_a = await create_tenant(db_session, "repo-h-a")
        user_a = await create_user(db_session, tenant_a)
        await db_session.commit()

        token = generate_opaque_token()
        recovery = PasswordRecoveryToken(
            tenant_id=tenant_a.id,
            user_id=user_a.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )
        db_session.add(recovery)
        await db_session.commit()

        # Look it up cross-tenant
        lookup = AuthTokenLookupRepository(db_session)
        found = await lookup.find_recovery_by_hash(hash_token(token))

        assert found is not None
        assert found.user_id == user_a.id


class TestAppStartup:
    """Test application bootstrap and lifespan."""

    async def test_app_startup_creates_engine_and_registers_routers(
        self, db_engine: None
    ) -> None:
        """APP STARTUP: app should initialize with engine and routers."""
        from app.main import create_app

        app = create_app()

        # Verify routers are registered
        routes = [route.path for route in app.routes]
        assert any("/api/auth" in route for route in routes)
        assert any("health" in route for route in routes)

    async def test_app_has_openapi_docs(self, db_engine: None) -> None:
        """APP STARTUP: app should have OpenAPI documentation available."""
        from app.main import create_app
        from httpx import ASGITransport, AsyncClient

        app = create_app()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/openapi.json")
            assert response.status_code == 200
            openapi = response.json()
            assert openapi["info"]["title"] == "activia-trace"
            assert openapi["info"]["version"] == "0.1.0"
