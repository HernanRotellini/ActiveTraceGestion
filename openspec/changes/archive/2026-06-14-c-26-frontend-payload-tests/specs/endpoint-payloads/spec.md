## ADDED Requirements

### Requirement: Contract test for Carrera payload alignment
The system SHALL validate that the frontend CarreraPayload (only `codigo` + `nombre`) matches the backend CarreraCreate schema.

#### Scenario: Sending correct Carrera payload returns 201
- **WHEN** a POST request to `/api/admin/carreras` sends `{"codigo": "TST-1", "nombre": "Test"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Carrera payload with `descripcion` returns 422
- **WHEN** a POST request to `/api/admin/carreras` sends `{"codigo": "TST-1", "nombre": "Test", "descripcion": "something"}`
- **THEN** the response SHALL have status 422

#### Scenario: Sending Carrera payload with `activo` returns 422
- **WHEN** a POST request to `/api/admin/carreras` sends `{"codigo": "TST-1", "nombre": "Test", "activo": true}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for Cohorte payload alignment
The system SHALL validate that the frontend CohortePayload matches the backend CohorteCreate schema.

#### Scenario: Sending correct Cohorte payload returns 201
- **WHEN** a POST request to `/api/admin/cohortes` sends `{"carrera_id": "<uuid>", "nombre": "2026A", "anio": 2026, "vig_desde": "2026-01-01"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Cohorte payload with `activo` returns 422
- **WHEN** a POST request to `/api/admin/cohortes` sends `{"carrera_id": "<uuid>", "nombre": "2026A", "anio": 2026, "vig_desde": "2026-01-01", "activo": true}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for Materia payload alignment
The system SHALL validate that the frontend MateriaPayload (only `codigo` + `nombre`) matches the backend MateriaCreate schema.

#### Scenario: Sending correct Materia payload returns 201
- **WHEN** a POST request to `/api/admin/materias` sends `{"codigo": "MAT-101", "nombre": "Matematicas"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Materia payload with `carrera_id` returns 422
- **WHEN** a POST request to `/api/admin/materias` sends `{"codigo": "MAT-101", "nombre": "Matematicas", "carrera_id": "<uuid>"}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for Usuario payload alignment
The system SHALL validate that the payload the frontend sends for user creation matches the backend UsuarioCreate schema.

#### Scenario: Sending correct Usuario payload returns 201
- **WHEN** a POST request to `/api/admin/usuarios` sends `{"nombre": "Juan", "apellidos": "Perez", "email": "juan@test.com", "cuil": "20-12345678-9"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Usuario payload with `password` returns 422
- **WHEN** a POST request to `/api/admin/usuarios` sends `{"nombre": "Juan", "apellidos": "Perez", "email": "juan@test.com", "password": "secret"}`
- **THEN** the response SHALL have status 422

#### Scenario: Sending Usuario payload with `roles` returns 422
- **WHEN** a POST request to `/api/admin/usuarios` sends `{"nombre": "Juan", "apellidos": "Perez", "email": "juan@test.com", "roles": ["ADMIN"]}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for Tarea payload alignment
The system SHALL validate that the frontend TareaPayload matches the backend TareaCreate schema.

#### Scenario: Sending correct Tarea payload returns 201
- **WHEN** a POST request to `/api/tareas` sends `{"titulo": "Revisar", "descripcion": "Revisar examenes", "asignado_a": "<uuid>"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Tarea payload with `prioridad` returns 422
- **WHEN** a POST request to `/api/tareas` sends `{"titulo": "Revisar", "descripcion": "Revisar", "asignado_a": "<uuid>", "prioridad": "alta"}`
- **THEN** the response SHALL have status 422

#### Scenario: Sending Tarea payload with `asignado_id` instead of `asignado_a` returns 422
- **WHEN** a POST request to `/api/tareas` sends `{"titulo": "Revisar", "descripcion": "Revisar", "asignado_id": "<uuid>"}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for SalarioBase payload alignment
The system SHALL validate that the frontend SalarioBasePayload matches the backend SalarioBaseCreate schema.

#### Scenario: Sending correct SalarioBase payload returns 201
- **WHEN** a POST request to `/api/liquidaciones/grilla/bases` sends `{"rol": "tutor", "monto": "1000.00", "desde": "2026-01-01"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending SalarioBase payload with `importe` instead of `monto` returns 422
- **WHEN** a POST request to `/api/liquidaciones/grilla/bases` sends `{"rol": "tutor", "importe": 1000, "desde": "2026-01-01"}`
- **THEN** the response SHALL have status 422

#### Scenario: Sending SalarioBase payload with `vigencia_desde` instead of `desde` returns 422
- **WHEN** a POST request to `/api/liquidaciones/grilla/bases` sends `{"rol": "tutor", "monto": "1000.00", "vigencia_desde": "2026-01-01"}`
- **THEN** the response SHALL have status 422

### Requirement: Contract test for SalarioPlus payload alignment
The system SHALL validate that the frontend PlusPayload matches the backend SalarioPlusCreate schema.

#### Scenario: Sending correct Plus payload returns 201
- **WHEN** a POST request to `/api/liquidaciones/grilla/pluses` sends `{"rol": "tutor", "grupo": "antiguedad", "descripcion": "Antiguedad 5 años", "monto": "500.00", "desde": "2026-01-01"}`
- **THEN** the response SHALL have status 201

#### Scenario: Sending Plus payload with `clave` instead of `grupo` returns 422
- **WHEN** a POST request to `/api/liquidaciones/grilla/pluses` sends `{"rol": "tutor", "clave": "antiguedad", "descripcion": "Antiguedad", "monto": "500.00", "desde": "2026-01-01"}`
- **THEN** the response SHALL have status 422

#### Scenario: Sending Plus payload with `vigencia_desde` instead of `desde` returns 422
- **WHEN** a POST request to `/api/liquidaciones/grilla/pluses` sends `{"rol": "tutor", "grupo": "antiguedad", "descripcion": "Antiguedad", "monto": "500.00", "vigencia_desde": "2026-01-01"}`
- **THEN** the response SHALL have status 422
