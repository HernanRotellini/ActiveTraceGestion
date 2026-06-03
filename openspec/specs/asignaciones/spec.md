## ADDED Requirements

### Requirement: Admin and coordinator can manage asignaciones
The system SHALL provide CRUD operations for Asignacion entities (Usuario ↔ Rol ↔ academic context) scoped to the authenticated user's tenant.

#### Scenario: Create a new asignacion
- **WHEN** a user with `equipos:asignar` sends a POST to `/api/asignaciones` with `{ "usuario_id": "<uuid>", "rol": "PROFESOR", "materia_id": "<uuid>", "carrera_id": "<uuid>", "cohorte_id": "<uuid>", "comisiones": ["A", "B"], "desde": "2026-03-01", "hasta": "2026-12-31" }`
- **THEN** the system creates a new Asignacion with `estado_vigencia: "vigente"` (derived from dates) and returns 201 with the full record

#### Scenario: Create asignacion without academic context (global role)
- **WHEN** a user with `equipos:asignar` sends a POST to `/api/asignaciones` with `{ "usuario_id": "<uuid>", "rol": "ADMIN", "desde": "2026-01-01" }` (no materia/carrera/cohorte)
- **THEN** the system creates a tenant-global assignment successfully (201)

#### Scenario: Create asignacion with responsable
- **WHEN** a user with `equipos:asignar` sends a POST to `/api/asignaciones` with `{ "usuario_id": "<uuid>", "rol": "PROFESOR", "responsable_id": "<uuid>", "materia_id": "<uuid>", "desde": "2026-03-01" }`
- **THEN** the system creates the assignment with the responsable reference and returns 201

#### Scenario: List active asignaciones
- **WHEN** a user with `equipos:asignar` sends a GET to `/api/asignaciones`
- **THEN** the system returns all non-deleted asignaciones in the current tenant, each with computed `estado_vigencia` ("vigente" or "vencida")

#### Scenario: Filter asignaciones by context
- **WHEN** a user sends a GET to `/api/asignaciones?materia_id=<uuid>`
- **THEN** the system returns only asignaciones matching that materia within the tenant

#### Scenario: Get asignacion by id
- **WHEN** a user with `equipos:asignar` sends a GET to `/api/asignaciones/{id}`
- **THEN** the system returns the asignacion with computed `estado_vigencia`, or 404 if not found

#### Scenario: Update asignacion vigencia
- **WHEN** a user with `equipos:asignar` sends a PATCH to `/api/asignaciones/{id}` with `{ "hasta": "2027-03-01" }`
- **THEN** the system updates the `hasta` field and returns the updated record

#### Scenario: Soft delete an asignacion
- **WHEN** a user with `equipos:asignar` sends a DELETE to `/api/asignaciones/{id}`
- **THEN** the system sets `deleted_at` and returns 204; subsequent GET returns 404

### Requirement: Expired assignment does not authorize
An assignment whose vigencia has ended (hasta < today) SHALL NOT grant any permissions, but the record SHALL be preserved for historical reference.

#### Scenario: Expired assignment is visible but marked as vencida
- **WHEN** a user views an asignacion whose `hasta` date is before today
- **THEN** the response includes `estado_vigencia: "vencida"`

#### Scenario: Active assignment is marked as vigente
- **WHEN** a user views an asignacion whose `desde` <= today <= `hasta` (or `hasta` is null)
- **THEN** the response includes `estado_vigencia: "vigente"`

### Requirement: Multi-rol support
A single Usuario SHALL be able to hold multiple Asignaciones with different roles in different academic contexts simultaneously.

#### Scenario: User has profesor and coordinador roles
- **WHEN** a usuario has both a PROFESOR assignment in materia A and a COORDINADOR assignment in materia B
- **THEN** both assignments exist and are independent; the user holds both roles

### Requirement: Authorization guard for asignaciones
All Asignacion endpoints SHALL require the `equipos:asignar` permission.

#### Scenario: User without equipos:asignar gets 403
- **WHEN** a user without `equipos:asignar` sends any request to any `/api/asignaciones/*` endpoint
- **THEN** the system returns 403 Forbidden

### Requirement: Multi-tenant isolation for asignaciones
Data from different tenants SHALL never be accessible across tenant boundaries.

#### Scenario: Tenant A cannot see tenant B's asignaciones
- **WHEN** a user from tenant A sends a GET to `/api/asignaciones`
- **THEN** the response does NOT include any asignaciones belonging to tenant B
