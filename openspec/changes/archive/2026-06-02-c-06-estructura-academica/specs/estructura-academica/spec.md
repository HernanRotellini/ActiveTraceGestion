## ADDED Requirements

### Requirement: Admin can manage carreras
The system SHALL provide CRUD operations for Carrera entities scoped to the authenticated user's tenant.

#### Scenario: Create a new carrera
- **WHEN** an ADMIN sends a POST to `/api/admin/carreras` with `{ "codigo": "TUPAD", "nombre": "Tecnicatura en Programación y Análisis de Datos" }`
- **THEN** the system creates a new Carrera with `estado: "activa"` and returns 201 with the full record including `id`, `created_at`, `updated_at`

#### Scenario: Create carrera with duplicate codigo returns 409
- **WHEN** an ADMIN sends a POST to `/api/admin/carreras` with a `codigo` that already exists in the same tenant
- **THEN** the system returns 409 Conflict with an error message indicating the duplicate

#### Scenario: Create carrera with same codigo in different tenant succeeds
- **WHEN** an ADMIN from tenant B sends a POST with the same `codigo` as an existing carrera in tenant A
- **THEN** the system creates the carrera successfully (201)

#### Scenario: List active carreras
- **WHEN** an ADMIN sends a GET to `/api/admin/carreras`
- **THEN** the system returns a list of all non-deleted carreras in the current tenant

#### Scenario: Update a carrera name
- **WHEN** an ADMIN sends a PATCH to `/api/admin/carreras/{id}` with `{ "nombre": "New Name" }`
- **THEN** the system updates the nombre field and returns the updated record

#### Scenario: Toggle carrera to inactive
- **WHEN** an ADMIN sends a PATCH to `/api/admin/carreras/{id}` with `{ "estado": "inactiva" }`
- **THEN** the system updates estado and returns the updated record

#### Scenario: Soft delete a carrera
- **WHEN** an ADMIN sends a DELETE to `/api/admin/carreras/{id}`
- **THEN** the system sets `deleted_at` and returns 204; subsequent GET returns 404

### Requirement: Admin can manage cohortes
The system SHALL provide CRUD operations for Cohorte entities scoped to the tenant, linked to an active Carrera.

#### Scenario: Create a new cohorte
- **WHEN** an ADMIN sends a POST to `/api/admin/cohortes` with `{ "carrera_id": "<uuid>", "nombre": "MAR-2026", "anio": 2026, "vig_desde": "2026-03-01" }`
- **THEN** the system creates a new Cohorte with `estado: "activa"` and returns 201

#### Scenario: Create cohorte on inactive carrera returns 409
- **WHEN** an ADMIN sends a POST to `/api/admin/cohortes` with a `carrera_id` whose estado is "inactiva"
- **THEN** the system returns 409 Conflict with message "Cannot create cohorte on inactive carrera"

#### Scenario: Create cohorte on nonexistent carrera returns 404
- **WHEN** an ADMIN sends a POST to `/api/admin/cohortes` with a `carrera_id` that does not exist
- **THEN** the system returns 404 Not Found

#### Scenario: Create duplicate cohorte name in same carrera returns 409
- **WHEN** an ADMIN sends a POST to `/api/admin/cohortes` with the same `(carrera_id, nombre)` as an existing cohorte
- **THEN** the system returns 409 Conflict

#### Scenario: Same cohorte name in different carrera succeeds
- **WHEN** an ADMIN creates cohortes with the same `nombre` under different carreras
- **THEN** both creations succeed (201)

#### Scenario: List cohortes filtered by carrera
- **WHEN** an ADMIN sends a GET to `/api/admin/cohortes?carrera_id=<uuid>`
- **THEN** the system returns only cohortes belonging to that carrera within the tenant

### Requirement: Admin can manage materias
The system SHALL provide CRUD operations for Materia entities (tenant-scoped academic catalog).

#### Scenario: Create a new materia
- **WHEN** an ADMIN sends a POST to `/api/admin/materias` with `{ "codigo": "PROG_I", "nombre": "Programación I" }`
- **THEN** the system creates a new Materia with `estado: "activa"` and returns 201

#### Scenario: Create materia with duplicate codigo returns 409
- **WHEN** an ADMIN sends a POST to `/api/admin/materias` with a `codigo` that already exists in the same tenant
- **THEN** the system returns 409 Conflict

#### Scenario: Same codigo in different tenant succeeds
- **WHEN** an ADMIN from tenant B sends a POST with the same `codigo` as an existing materia in tenant A
- **THEN** the system creates the materia successfully (201)

#### Scenario: List materias
- **WHEN** an ADMIN sends a GET to `/api/admin/materias`
- **THEN** the system returns all non-deleted materias in the current tenant

### Requirement: Multi-tenant isolation
Data from different tenants SHALL never be accessible across tenant boundaries.

#### Scenario: Tenant A cannot see tenant B's carreras
- **WHEN** an ADMIN from tenant A sends a GET to `/api/admin/carreras`
- **THEN** the response does NOT include any carreras belonging to tenant B

#### Scenario: Tenant A cannot update tenant B's materia
- **WHEN** an ADMIN from tenant A sends a PATCH to `/api/admin/materias/{id}` where `id` belongs to tenant B
- **THEN** the system returns 404 Not Found

### Requirement: Authorization guard
All endpoints SHALL require the `estructura:gestionar` permission.

#### Scenario: User without estructura:gestionar gets 403
- **WHEN** a user without `estructura:gestionar` sends any request to any `/api/admin/carreras/*`, `/api/admin/cohortes/*`, or `/api/admin/materias/*` endpoint
- **THEN** the system returns 403 Forbidden
