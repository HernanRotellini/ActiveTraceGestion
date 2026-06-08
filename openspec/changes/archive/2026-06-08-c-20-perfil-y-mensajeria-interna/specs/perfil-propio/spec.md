# perfil-propio Specification

## Purpose
Allow any authenticated user to view and update their own profile information (name, contact details, bank data, regional preferences, tax status) while protecting sensitive fields (CUIL) from self-modification.

## ADDED Requirements

### Requirement: View own profile
The system SHALL allow any authenticated user to retrieve their own profile data.

#### Scenario: Get own profile
- **WHEN** an authenticated user sends a GET to `/api/v1/perfil`
- **THEN** the system returns 200 with all profile fields (nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, regional, modalidad_cobro, genero, condicion_impositiva, matricula_profesional, telefono, direccion, facturador)

#### Scenario: Profile includes PII decrypted
- **WHEN** an authenticated user views their profile
- **THEN** PII fields (email, dni, cuil, cbu, alias_cbu) are returned in plaintext (decrypted from storage)

### Requirement: Update own profile
The system SHALL allow any authenticated user to update their own editable profile fields.

#### Scenario: Update editable fields
- **WHEN** an authenticated user sends a PUT to `/api/v1/perfil` with `{ "nombre": "New", "banco": "Banco Nación", "cbu": "00000031000000000002", "alias_cbu": "NEW.ALIAS", "regional": "Córdoba", "modalidad_cobro": "liquidacion", "telefono": "3511234567" }`
- **THEN** the system returns 200 with the updated profile, reflecting all changes

#### Scenario: CUIL is not modifiable
- **WHEN** an authenticated user sends a PUT to `/api/v1/perfil` with `{ "cuil": "20-99999999-9" }`
- **THEN** the system returns 422 and the cuil field is NOT updated

#### Scenario: Partial update only changes provided fields
- **WHEN** an authenticated user sends a PUT to `/api/v1/perfil` with only `{ "telefono": "3519999999" }`
- **THEN** the system only updates telefono and leaves other fields unchanged

#### Scenario: Cannot edit another user's profile
- **WHEN** a user attempts to access `/api/v1/perfil` while authenticated as a different user
- **THEN** the system returns their own profile, not the other user's (identity always from JWT)

### Requirement: Profile validation
The system SHALL validate profile fields on update.

#### Scenario: Invalid CBU format rejected
- **WHEN** an authenticated user sends a PUT with `{ "cbu": "invalid" }`
- **THEN** the system returns 422 with validation error

#### Scenario: Email uniqueness across tenant
- **WHEN** an authenticated user sends a PUT with an email that already exists for another user in the same tenant
- **THEN** the system returns 409 Conflict
