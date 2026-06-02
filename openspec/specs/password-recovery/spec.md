# password-recovery Specification

## Purpose
TBD - created by archiving change c-03-auth-jwt-2fa. Update Purpose after archive.
## Requirements
### Requirement: Password recovery request
The system SHALL generate a one-use password recovery token for an existing active user email.

#### Scenario: Recovery request creates token
- **WHEN** an active user requests password recovery with their email
- **THEN** the system creates a short-lived one-use recovery token

#### Scenario: Recovery request does not reveal account existence
- **WHEN** password recovery is requested for an unknown email
- **THEN** the system returns a generic response without issuing a usable token

### Requirement: Password reset token use
The system SHALL allow a password reset only with a valid unexpired unused recovery token.

#### Scenario: Valid token resets password once
- **WHEN** a user submits a valid recovery token and new password
- **THEN** the system updates the password hash and marks the token used

#### Scenario: Used token is rejected
- **WHEN** a recovery token has already been used
- **THEN** the system rejects any further reset attempt with that token

#### Scenario: Expired token is rejected
- **WHEN** a recovery token is expired
- **THEN** the system rejects the password reset

