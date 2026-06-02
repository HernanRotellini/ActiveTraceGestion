## ADDED Requirements

### Requirement: Permission resolution from authenticated roles
The system SHALL resolve the effective permissions for an authenticated user from their roles, scoped by tenant, on each protected request (no caching in JWT).

#### Scenario: Permissions resolved after authentication
- **WHEN** a user is authenticated and `require_permission` evaluates their access
- **THEN** the effective permissions are computed from the union of all enabled role-permission assignments

#### Scenario: Permission change takes effect without re-login
- **WHEN** a user's role-permission assignment changes
- **THEN** the next protected request uses the updated permissions
