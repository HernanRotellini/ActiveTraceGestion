## ADDED Requirements

### Requirement: Admin can manage usuarios
The system SHALL provide CRUD operations for Usuario entities scoped to the authenticated user's tenant, with automatic AES-256 encryption of PII fields at rest.

#### Scenario: Create a new usuario
- **WHEN** an ADMIN sends a POST to `/api/admin/usuarios` with `{ "nombre": "Juan", "apellidos": "Perez", "email": "juan@example.com", "dni": "12345678", "cuil": "20-12345678-9", "cbu": "00000031000000000001", "alias_cbu": "JUAN.PEREZ.ALIAS" }`
- **THEN** the system creates a new Usuario with `estado: "activo"` and returns 201 with the full record including `id`, `created_at`, `updated_at`, with email, dni, cuil, cbu, alias_cbu in plaintext (decrypted for the response)

#### Scenario: Create usuario with duplicate email returns 409
- **WHEN** an ADMIN sends a POST to `/api/admin/usuarios` with an `email` that already exists in the same tenant
- **THEN** the system returns 409 Conflict with an error message indicating the duplicate

#### Scenario: Same email in different tenant succeeds
- **WHEN** an ADMIN from tenant B sends a POST with the same `email` as an existing usuario in tenant A
- **THEN** the system creates the usuario successfully (201)

#### Scenario: PII fields are encrypted at rest
- **WHEN** an usuario is created with PII fields (email, dni, cuil, cbu, alias_cbu)
- **THEN** the rows in the `usuarios` table contain ciphertext (base64-encoded) for those fields, not the original plaintext values

#### Scenario: List usuarios
- **WHEN** an ADMIN sends a GET to `/api/admin/usuarios`
- **THEN** the system returns a list of all non-deleted usuarios in the current tenant, with PII fields decrypted in the response

#### Scenario: Get usuario by id
- **WHEN** an ADMIN sends a GET to `/api/admin/usuarios/{id}`
- **THEN** the system returns the usuario with all fields decrypted, or 404 if not found

#### Scenario: Update usuario fields
- **WHEN** an ADMIN sends a PATCH to `/api/admin/usuarios/{id}` with `{ "nombre": "New Name", "email": "new@example.com" }`
- **THEN** the system updates the provided fields, re-encrypts any changed PII fields, and returns the updated record

#### Scenario: Toggle usuario to inactive
- **WHEN** an ADMIN sends a PATCH to `/api/admin/usuarios/{id}` with `{ "estado": "inactivo" }`
- **THEN** the system updates estado and returns the updated record

#### Scenario: Soft delete a usuario
- **WHEN** an ADMIN sends a DELETE to `/api/admin/usuarios/{id}`
- **THEN** the system sets `deleted_at` and returns 204; subsequent GET returns 404

#### Scenario: PII is not exposed in log messages
- **WHEN** any operation on a usuario causes an error
- **THEN** the error log does not contain PII fields in plaintext

### Requirement: Authorization guard for usuarios
All Usuario endpoints SHALL require the `usuarios:gestionar` permission.

#### Scenario: User without usuarios:gestionar gets 403
- **WHEN** a user without `usuarios:gestionar` sends any request to any `/api/admin/usuarios/*` endpoint
- **THEN** the system returns 403 Forbidden

### Requirement: Multi-tenant isolation for usuarios
Data from different tenants SHALL never be accessible across tenant boundaries.

#### Scenario: Tenant A cannot see tenant B's usuarios
- **WHEN** an ADMIN from tenant A sends a GET to `/api/admin/usuarios`
- **THEN** the response does NOT include any usuarios belonging to tenant B

#### Scenario: Tenant A cannot update tenant B's usuario
- **WHEN** an ADMIN from tenant A sends a PATCH to `/api/admin/usuarios/{id}` where `id` belongs to tenant B
- **THEN** the system returns 404 Not Found
