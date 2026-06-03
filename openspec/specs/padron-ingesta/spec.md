## ADDED Requirements

### Requirement: VersionPadron model
The system SHALL maintain a versioned registry of enrolled students per `(materia_id, cohorte_id)`. Each import creates a new `VersionPadron` record. Only one version SHALL be active per `(materia_id, cohorte_id)` at any time. Activating a new version SHALL automatically deactivate the previously active version in the same transaction.

#### Scenario: Create first version activates it
- **WHEN** a user imports a padron for `(materia_id=X, cohorte_id=Y)` for the first time
- **THEN** a `VersionPadron` is created with `activa=true`

#### Scenario: Second import deactivates first
- **WHEN** a user imports a new padron for the same `(materia_id=X, cohorte_id=Y)`
- **THEN** the previous active version is set to `activa=false` and the new version is `activa=true`

#### Scenario: Version history is preserved
- **WHEN** querying versions for `(materia_id=X, cohorte_id=Y)` after 3 imports
- **THEN** 3 `VersionPadron` records exist, with only the latest having `activa=true`

### Requirement: EntradaPadron model
Each `VersionPadron` SHALL contain multiple `EntradaPadron` records representing individual students. An `EntradaPadron` SHALL have `usuario_id` as nullable (student may not have a system account yet). Email SHALL be stored encrypted (AES-256). Name, surnames, comision, and regional SHALL be in plain text.

#### Scenario: EntradaPadron without usuario_id
- **WHEN** importing a padron entry for a student without a user account
- **THEN** the `EntradaPadron` is created with `usuario_id=NULL` and the student's personal data

#### Scenario: Email is encrypted at rest
- **WHEN** querying the database directly
- **THEN** the `email` field in `EntradaPadron` SHALL appear as ciphertext

### Requirement: Import padron from file with preview
The system SHALL provide a two-step import flow: (1) preview and (2) confirm. Step 1 SHALL accept an `.xlsx` or `.csv` file, parse it, detect columns (mapping to: nombre, apellidos, email, comision, regional), and return a preview with column mapping, sample rows, and total row count. Step 2 SHALL accept a preview token to confirm and persist the data.

#### Scenario: Successful xlsx import with preview
- **WHEN** a user uploads a valid `.xlsx` file with columns `[nombre, apellidos, email, comision]`
- **THEN** the system returns a preview with detected columns, first 5 rows, and total count

#### Scenario: Preview token used for confirmation
- **WHEN** a user confirms import using the preview token
- **THEN** a new `VersionPadron` is created, all parsed entries are persisted as `EntradaPadron`, and the version is set as active

#### Scenario: Preview token expires
- **WHEN** a user attempts to confirm with an expired preview token
- **THEN** the system returns 409 Conflict with message indicating token expired

#### Scenario: CSV with alternative delimiter
- **WHEN** a user uploads a `.csv` file with semicolon delimiter
- **THEN** the system SHALL auto-detect the delimiter and parse correctly

#### Scenario: Malformed file returns descriptive error
- **WHEN** a user uploads a malformed file with missing required columns
- **THEN** the system returns 422 with details about which columns are missing

### Requirement: Vaciar datos de materia
The system SHALL allow a user to delete their padron data for a specific materia. The operation SHALL soft-delete all `VersionPadron` records created by that user for the materia. It SHALL NOT affect versions created by other users (RN-04 scope isolation).

#### Scenario: Teacher clears their own data
- **WHEN** a teacher calls vaciar for `materia_id=X`
- **THEN** all `VersionPadron` records created by that teacher for materia X are soft-deleted

#### Scenario: Other teacher's data is preserved
- **WHEN** teacher A clears data for `materia_id=X`
- **THEN** teacher B's padron versions for the same materia remain active

### Requirement: Audit trail
Every padron import operation SHALL generate an audit log entry with code `PADRON_CARGAR`, recording actor ID, materia ID, cohorte ID, version ID, and entry count.

#### Scenario: Import generates audit entry
- **WHEN** a padron import is confirmed
- **THEN** an audit log entry is created with action `PADRON_CARGAR`, including actor, materia, cohorte, version_id, and entry_count

#### Scenario: Vaciar generates audit entry
- **WHEN** a user calls vaciar for a materia
- **THEN** an audit log entry is created recording the action and affected materia

### Requirement: Tenant isolation
All padron data SHALL be isolated by tenant. A query for padron versions in tenant A SHALL NOT return data from tenant B.

#### Scenario: Tenant isolation on query
- **WHEN** querying padron versions for a materia in tenant A
- **THEN** only versions belonging to tenant A are returned, even if tenant B has versions for the same materia UUID
