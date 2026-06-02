# rbac-core Specification

## Purpose
TBD - created by archiving change c-04-rbac-permisos-finos. Update Purpose after archive.
## Requirements
### Requirement: Role catalog
The system SHALL provide a catalog of roles administrable per tenant. Each role has a unique code and a human-readable name.

#### Scenario: Default roles exist after migration
- **WHEN** the 003 migration runs
- **THEN** the `rol` table contains ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS

#### Scenario: Role is tenant-scoped
- **WHEN** a role is created
- **THEN** it belongs to exactly one tenant and cannot be accessed by other tenants

### Requirement: Permission catalog
The system SHALL provide a catalog of atomic permissions with format `modulo:accion`. Each permission has a unique code and description.

#### Scenario: Permissions are defined as modulo:accion
- **WHEN** a permission is created
- **THEN** its code follows the format `<modulo>:<accion>` (e.g., `calificaciones:importar`)

#### Scenario: Default permissions exist after migration
- **WHEN** the 003 migration runs
- **THEN** all permissions from the 03_actores_y_roles.md §3.3 matrix are loaded

### Requirement: Role-permission matrix
The system SHALL support assigning permissions to roles via a many-to-many matrix with enable/disable flag and scope (global vs propio).

#### Scenario: Permission is assignable to role
- **WHEN** a permission is assigned to a role with `habilitado = true`
- **THEN** users with that role have the effective permission

#### Scenario: Permission can be disabled per role
- **WHEN** a permission assigned to a role has `habilitado = false`
- **THEN** users with that role do NOT have the effective permission

### Requirement: Effective permission resolution
The system SHALL compute effective permissions for an authenticated user as the union of all enabled permissions from all their roles, scoped by tenant.

#### Scenario: Union of multiple roles
- **WHEN** a user has roles PROFESOR and COORDINADOR
- **THEN** the effective permissions include the union of both role's permissions

#### Scenario: Tenant isolation
- **WHEN** two users from different tenants have the same role
- **THEN** each user only sees permissions scoped to their own tenant

### Requirement: Authorization check
The system SHALL verify that an authenticated user holds a specific `modulo:accion` permission before allowing access to a protected resource.

#### Scenario: User with permission is authorized
- **WHEN** an authenticated user holds the required permission
- **THEN** access is granted

#### Scenario: User without permission is denied
- **WHEN** an authenticated user does NOT hold the required permission
- **THEN** access is denied with status 403

#### Scenario: Unauthenticated user is denied
- **WHEN** a request has no valid session
- **THEN** access is denied with status 401 (before permission check)

