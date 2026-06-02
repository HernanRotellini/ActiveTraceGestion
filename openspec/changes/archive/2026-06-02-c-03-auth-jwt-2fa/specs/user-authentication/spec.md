## ADDED Requirements

### Requirement: Password login
The system SHALL authenticate active tenant users with email, password and anonymous pre-session `tenant_code` using Argon2id password hashes.

#### Scenario: Successful login issues session tokens
- **WHEN** an active user submits a valid email and password
- **THEN** the system returns a signed access token and a refresh token

#### Scenario: Login resolves tenant from tenant code
- **WHEN** a login request includes `tenant_code`
- **THEN** the system resolves the tenant server-side before credential lookup and does not accept tenant context from authenticated requests after login

#### Scenario: Invalid password is rejected
- **WHEN** a user submits a valid email with an invalid password
- **THEN** the system rejects the login without issuing any session token

#### Scenario: Inactive user is rejected
- **WHEN** an inactive user submits valid credentials
- **THEN** the system rejects the login without issuing any session token

### Requirement: Access token claims
The system SHALL issue access JWTs with only minimal identity claims and no permissions.

#### Scenario: Token contains minimal claims
- **WHEN** a successful login issues an access token
- **THEN** the token contains user id, tenant id, roles and expiration

#### Scenario: Token omits permissions
- **WHEN** an access token is decoded
- **THEN** it does not contain effective permissions

### Requirement: Current user dependency
The system SHALL resolve the current user and tenant exclusively from a verified access token.

#### Scenario: Valid token resolves user context
- **WHEN** a protected dependency receives a valid access token for an active user
- **THEN** it returns the user identity and tenant from the token

#### Scenario: Request parameters cannot alter identity
- **WHEN** a request includes user id or tenant id parameters that differ from the verified token
- **THEN** the dependency keeps the identity and tenant from the token only

#### Scenario: Invalid token fails closed
- **WHEN** a token is expired, malformed or signed with the wrong secret
- **THEN** the dependency rejects the request as unauthenticated

### Requirement: Logout revokes refresh session
The system SHALL allow an authenticated session to be logged out by revoking its refresh session.

#### Scenario: Logout revokes active refresh token
- **WHEN** a user logs out with an active refresh token
- **THEN** the refresh token can no longer be used to obtain new tokens
