## Requirements

### Requirement: AES-256 encryption helper
The system SHALL provide a centralized helper to encrypt and decrypt sensitive values at rest using AES-256-compatible key material from configuration.

#### Scenario: Sensitive value round-trips
- **WHEN** a plaintext sensitive value is encrypted and then decrypted with the configured key
- **THEN** the decrypted value equals the original plaintext

#### Scenario: Ciphertext differs from plaintext
- **WHEN** a plaintext sensitive value is encrypted
- **THEN** the stored ciphertext does not contain the plaintext value

### Requirement: Encryption key validation
The system SHALL validate encryption key configuration before encrypting or decrypting values.

#### Scenario: Valid key is accepted
- **WHEN** `ENCRYPTION_KEY` contains valid 32-byte key material
- **THEN** encryption and decryption operations can proceed

#### Scenario: Invalid key fails closed
- **WHEN** `ENCRYPTION_KEY` is missing or has invalid length
- **THEN** the system rejects encryption setup instead of using an insecure fallback

### Requirement: Sensitive values are not logged in plaintext
The system SHALL avoid exposing plaintext sensitive values through encryption helper errors or representations.

#### Scenario: Encryption failure does not leak plaintext
- **WHEN** encryption of a sensitive value fails
- **THEN** the raised/loggable error message does not include the plaintext value

#### Scenario: Decryption failure does not leak ciphertext-derived secrets
- **WHEN** decryption fails for malformed ciphertext
- **THEN** the raised/loggable error message does not include decrypted partial data or sensitive plaintext
