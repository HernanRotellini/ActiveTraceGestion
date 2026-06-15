"""Primitivas de seguridad para autenticación."""

import base64
import hashlib
import hmac
import os
import struct
import time
from datetime import UTC, datetime, timedelta
from uuid import UUID

from argon2 import PasswordHasher
from jose import JWTError, jwt

from app.core.config import Settings

_password_hasher = PasswordHasher()


class TokenError(ValueError):
    """Token inválido o expirado."""


def hash_password(password: str) -> str:
    """Hashea password con Argon2id."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica password contra hash Argon2id sin filtrar detalle."""
    try:
        return _password_hasher.verify(password_hash, password)
    except Exception:
        return False


def generate_opaque_token() -> str:
    """Genera token opaco portable."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode("ascii").rstrip("=")


def hash_token(token: str) -> str:
    """Hasher estable para verificadores de tokens sensibles."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    *, user_id: UUID, tenant_id: UUID, roles: list[str], email: str, settings: Settings, expires_delta: timedelta | None = None
) -> str:
    """Crea JWT de acceso con claims mínimos."""
    expires_at = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    claims = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "email": email,
        "exp": expires_at,
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm="HS256")


def verify_access_token(token: str, settings: Settings) -> dict:
    """Verifica JWT y devuelve claims mínimos validados."""
    try:
        claims = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        required = {"sub", "user_id", "tenant_id", "roles", "exp"}
        if not required.issubset(claims) or claims["sub"] != claims["user_id"]:
            raise TokenError("invalid access token")
        return claims
    except (JWTError, ValueError, TypeError) as exc:
        raise TokenError("invalid access token") from exc


def generate_totp_secret() -> str:
    """Genera secreto TOTP base32."""
    return base64.b32encode(os.urandom(20)).decode("ascii").rstrip("=")


def totp_code(secret: str, *, now: int | None = None, step: int = 30) -> str:
    """Calcula código TOTP RFC 6238 usando SHA1."""
    padded = secret + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded, casefold=True)
    counter = int((now or time.time()) // step)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{code % 1_000_000:06d}"


def verify_totp(secret: str, code: str) -> bool:
    """Verifica TOTP con tolerancia de una ventana."""
    now = int(time.time())
    return any(hmac.compare_digest(totp_code(secret, now=now + offset), code) for offset in (-30, 0, 30))
