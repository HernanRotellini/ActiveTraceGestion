# usuarios Specification — Delta

## MODIFIED Requirements

### Requirement: Admin can manage usuarios
The system SHALL provide CRUD operations for Usuario entities scoped to the authenticated user's tenant, with automatic AES-256 encryption of PII fields at rest. The Usuario model SHALL include the following additional profile fields: `regional`, `modalidad_cobro`, `genero`, `condicion_impositiva`, `matricula_profesional`.

#### Scenario: Create a new usuario (unchanged)
- **WHEN** an ADMIN sends a POST to `/api/admin/usuarios` with the required fields
- **THEN** the system creates a new Usuario with `estado: "activo"` and returns 201

#### Scenario: New profile fields are included in response (ADDED)
- **WHEN** an ADMIN retrieves a usuario
- **THEN** the response includes `regional`, `modalidad_cobro`, `genero`, `condicion_impositiva`, and `matricula_profesional` fields

#### Scenario: New profile fields can be set on create (ADDED)
- **WHEN** an ADMIN creates a usuario with `{ "regional": "Córdoba", "modalidad_cobro": "liquidacion" }`
- **THEN** the fields are stored and returned in the response
