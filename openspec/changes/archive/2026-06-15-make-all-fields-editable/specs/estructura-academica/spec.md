## MODIFIED Requirements

### Requirement: Admin can manage carreras
The system SHALL provide CRUD operations for Carrera entities scoped to the authenticated user's tenant.
(No change to requirement text, but scenarios below are updated)

#### Scenario: Create a new carrera with optional description
- **WHEN** an ADMIN sends a POST to `/api/admin/carreras` with `{ "codigo": "TUPAD", "nombre": "Tecnicatura en Programación", "descripcion": "Nueva tecnicatura" }`
- **THEN** the system creates a new Carrera with the provided `descripcion` and returns 201

#### Scenario: Create a new carrera without description
- **WHEN** an ADMIN sends a POST to `/api/admin/carreras` with `{ "codigo": "TUPAD", "nombre": "Tecnicatura" }` (no `descripcion`)
- **THEN** the system creates a new Carrera with `descripcion: ""` and returns 201

#### Scenario: Update a carrera name and description
- **WHEN** an ADMIN sends a PATCH to `/api/admin/carreras/{id}` with `{ "nombre": "New Name", "descripcion": "Updated description" }`
- **THEN** the system updates both `nombre` and `descripcion` fields and returns the updated record

#### Scenario: Update a carrera codigo
- **WHEN** an ADMIN sends a PATCH to `/api/admin/carreras/{id}` with `{ "codigo": "NEW-CODE" }`
- **THEN** the system updates the `codigo` field and returns the updated record

### Requirement: Admin can manage materias
The system SHALL provide CRUD operations for Materia entities (tenant-scoped academic catalog).
(No change to requirement text, but scenarios below are updated)

#### Scenario: Update a materia name, codigo, and carga_horaria
- **WHEN** an ADMIN sends a PATCH to `/api/admin/materias/{id}` with `{ "nombre": "New Name", "codigo": "NEW-CODE", "carga_horaria": 120 }`
- **THEN** the system updates all provided fields and returns the updated record

#### Scenario: Update materia codigo to an existing one returns 409
- **WHEN** an ADMIN sends a PATCH to `/api/admin/materias/{id}` with a `codigo` that already exists in the same tenant
- **THEN** the system returns 409 Conflict with a duplicate error message
