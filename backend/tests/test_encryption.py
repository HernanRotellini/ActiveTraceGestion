"""Tests TDD para cifrado de datos sensibles en reposo."""

import pytest

from app.core.encryption import (
    EncryptionError,
    EncryptionKeyError,
    decrypt_sensitive_value,
    encrypt_sensitive_value,
    validate_encryption_key,
)


VALID_KEY = "a" * 32


class TestEncryptionRoundTrip:
    """Contrato de cifrado/descifrado AES-256."""

    def test_sensitive_value_round_trips(self) -> None:
        plaintext = "dni-12345678"

        ciphertext = encrypt_sensitive_value(plaintext, encryption_key=VALID_KEY)

        assert decrypt_sensitive_value(ciphertext, encryption_key=VALID_KEY) == plaintext

    def test_ciphertext_differs_from_plaintext_and_does_not_contain_it(self) -> None:
        plaintext = "cbu-000123456789"

        ciphertext = encrypt_sensitive_value(plaintext, encryption_key=VALID_KEY)

        assert ciphertext != plaintext
        assert plaintext not in ciphertext


class TestEncryptionKeyValidation:
    """Validación fail-closed de clave de cifrado."""

    def test_valid_32_byte_key_is_accepted(self) -> None:
        assert validate_encryption_key(VALID_KEY) == b"a" * 32

    @pytest.mark.parametrize("invalid_key", [None, "", "short", "b" * 31, "c" * 33])
    def test_missing_or_invalid_key_is_rejected(self, invalid_key: str | None) -> None:
        with pytest.raises(EncryptionKeyError):
            validate_encryption_key(invalid_key)


class TestEncryptionErrorsDoNotLeakSensitiveValues:
    """Errores logueables no exponen plaintext ni ciphertext sensible."""

    def test_encryption_failure_does_not_include_plaintext(self) -> None:
        plaintext = "sensitive-value-\ud800"

        with pytest.raises(EncryptionError) as exc_info:
            encrypt_sensitive_value(plaintext, encryption_key=VALID_KEY)

        assert "sensitive-value" not in str(exc_info.value)

    def test_decryption_failure_does_not_include_ciphertext(self) -> None:
        malformed_ciphertext = "malformed-secret-ciphertext"

        with pytest.raises(EncryptionError) as exc_info:
            decrypt_sensitive_value(malformed_ciphertext, encryption_key=VALID_KEY)

        assert malformed_ciphertext not in str(exc_info.value)
        assert "secret" not in str(exc_info.value)
