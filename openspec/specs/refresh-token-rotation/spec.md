# refresh-token-rotation Specification

## Purpose
TBD - created by archiving change c-03-auth-jwt-2fa. Update Purpose after archive.
## Requirements
### Requirement: Refresh token rotation
The system SHALL rotate refresh tokens on every successful refresh request.

#### Scenario: Valid refresh rotates token
- **WHEN** a client submits a valid active refresh token
- **THEN** the system revokes the submitted token and returns a new access token plus a new refresh token

#### Scenario: Old refresh token cannot be reused
- **WHEN** a client submits a refresh token that was already rotated
- **THEN** the system rejects the request and does not issue new tokens

### Requirement: Refresh token storage
The system SHALL store refresh tokens as non-plaintext verifiers with expiration and revocation metadata.

#### Scenario: Stored refresh token is not plaintext
- **WHEN** a refresh token is issued
- **THEN** the database stores only a non-plaintext verifier and lifecycle metadata

#### Scenario: Expired refresh token is rejected
- **WHEN** a client submits an expired refresh token
- **THEN** the system rejects it and does not issue new tokens

### Requirement: Refresh tenant isolation
Refresh operations SHALL validate that the token belongs to the user and tenant encoded in the refresh session.

#### Scenario: Refresh preserves tenant context
- **WHEN** a refresh token is rotated
- **THEN** the new access token contains the same user and tenant context as the refresh session

