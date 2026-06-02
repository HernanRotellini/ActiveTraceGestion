"""Helpers de cifrado AES-256 para datos sensibles en reposo."""

import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class EncryptionKeyError(ValueError):
    """Error de configuración de clave de cifrado."""


class EncryptionError(ValueError):
    """Error seguro para operaciones de cifrado/descifrado."""


def validate_encryption_key(encryption_key: str | None) -> bytes:
    """Valida y retorna clave AES-256 como bytes."""
    if encryption_key is None:
        raise EncryptionKeyError("ENCRYPTION_KEY is required")
    key_bytes = encryption_key.encode("utf-8")
    if len(key_bytes) != 32:
        raise EncryptionKeyError("ENCRYPTION_KEY must be exactly 32 bytes")
    return key_bytes


def encrypt_sensitive_value(plaintext: str, *, encryption_key: str) -> str:
    """Cifra un valor sensible y retorna ciphertext portable."""
    try:
        key_bytes = validate_encryption_key(encryption_key)
        nonce = os.urandom(12)
        ciphertext = AESGCM(key_bytes).encrypt(nonce, plaintext.encode("utf-8"), None)
        return base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")
    except EncryptionKeyError:
        raise
    except Exception as exc:
        raise EncryptionError("Sensitive value encryption failed") from exc


def decrypt_sensitive_value(ciphertext: str, *, encryption_key: str) -> str:
    """Descifra un valor sensible previamente cifrado."""
    try:
        key_bytes = validate_encryption_key(encryption_key)
        payload = base64.urlsafe_b64decode(ciphertext.encode("ascii"))
        nonce = payload[:12]
        encrypted_value = payload[12:]
        plaintext = AESGCM(key_bytes).decrypt(nonce, encrypted_value, None)
        return plaintext.decode("utf-8")
    except EncryptionKeyError:
        raise
    except (InvalidTag, ValueError, UnicodeDecodeError) as exc:
        raise EncryptionError("Sensitive value decryption failed") from exc
