## ADDED Requirements

### Requirement: Permission guard as FastAPI dependency
The system SHALL provide a reusable FastAPI dependency `require_permission("modulo:accion")` that protects endpoints by evaluating the required permission against the authenticated user's effective permissions.

#### Scenario: Guard on endpoint grants access
- **WHEN** an endpoint is decorated with `require_permission("calificaciones:importar")` and the authenticated user has that permission
- **THEN** the request proceeds to the handler

#### Scenario: Guard on endpoint denies access
- **WHEN** an endpoint is decorated with `require_permission("calificaciones:importar")` and the authenticated user does NOT have that permission
- **THEN** the response is 403 Forbidden

#### Scenario: Guard requires authentication first
- **WHEN** an endpoint is decorated with `require_permission(...)` and no valid authentication is provided
- **THEN** the response is 401 Unauthorized (before permission check)

### Requirement: Permission constants for type safety
The system SHALL define permission codes as typed constants to avoid string literal typos in endpoint decorators.

#### Scenario: Constants match migration seed
- **WHEN** a permission constant is used in a decorator
- **THEN** its value matches the `codigo` column in the `permiso` table

### Requirement: No permission caching in JWT
The guard SHALL resolve permissions server-side on every request, never from the access token.

#### Scenario: Changed permissions take effect immediately
- **WHEN** a user's role permissions are modified (via admin UI in future change)
- **THEN** the new permissions apply on the next request without requiring re-login
