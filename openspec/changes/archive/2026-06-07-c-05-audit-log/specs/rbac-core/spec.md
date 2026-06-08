# rbac-core Specification

## MODIFIED Requirements

### Requirement: Permission catalog
The system SHALL provide a catalog of atomic permissions with format `modulo:accion`. Each permission has a unique code and description. The `impersonacion:usar` permission controls access to impersonation features.

#### Scenario: Permissions are defined as modulo:accion
- **WHEN** a permission is created
- **THEN** its code follows the format `<modulo>:<accion>` (e.g., `calificaciones:importar`)

#### Scenario: Default permissions exist after migration
- **WHEN** the 003 migration runs
- **THEN** all permissions from the 03_actores_y_roles.md §3.3 matrix are loaded

#### Scenario: Impersonation permission is required
- **WHEN** a user without `impersonacion:usar` attempts to impersonate another user
- **THEN** the request is denied with status 403
