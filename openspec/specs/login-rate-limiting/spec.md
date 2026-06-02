# login-rate-limiting Specification

## Purpose
TBD - created by archiving change c-03-auth-jwt-2fa. Update Purpose after archive.
## Requirements
### Requirement: Login attempt rate limit
The system SHALL limit login attempts to 5 attempts per 60 seconds per IP and email combination.

#### Scenario: Attempts within limit proceed
- **WHEN** an IP and email combination has fewer than 5 attempts in the current 60-second window
- **THEN** the system allows the credential check to proceed

#### Scenario: Sixth attempt is blocked
- **WHEN** an IP and email combination reaches a sixth login attempt within 60 seconds
- **THEN** the system rejects the attempt before credential validation

#### Scenario: Window expiry resets limit
- **WHEN** more than 60 seconds have elapsed since the tracked attempts
- **THEN** the system allows login attempts for that IP and email combination again

