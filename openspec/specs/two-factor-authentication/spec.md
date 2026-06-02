# two-factor-authentication Specification

## Purpose
TBD - created by archiving change c-03-auth-jwt-2fa. Update Purpose after archive.
## Requirements
### Requirement: TOTP enrollment
The system SHALL allow a user to enroll a TOTP second factor by generating and verifying a shared secret.

#### Scenario: Enrollment creates pending secret
- **WHEN** an authenticated user requests TOTP enrollment
- **THEN** the system creates a pending TOTP secret without enabling 2FA yet

#### Scenario: Valid TOTP verification enables 2FA
- **WHEN** the user verifies the pending secret with a valid TOTP code
- **THEN** the system enables 2FA for that user

### Requirement: 2FA login gate
The system SHALL require TOTP verification after valid password credentials when 2FA is enabled.

#### Scenario: Password login with 2FA returns challenge
- **WHEN** a 2FA-enabled user submits valid email and password
- **THEN** the system returns a temporary 2FA challenge instead of access and refresh tokens

#### Scenario: Valid TOTP challenge issues session
- **WHEN** the user submits a valid TOTP code for an active challenge
- **THEN** the system issues an access token and refresh token

#### Scenario: Invalid TOTP challenge is rejected
- **WHEN** the user submits an invalid or expired TOTP code
- **THEN** the system rejects the challenge and does not issue session tokens

