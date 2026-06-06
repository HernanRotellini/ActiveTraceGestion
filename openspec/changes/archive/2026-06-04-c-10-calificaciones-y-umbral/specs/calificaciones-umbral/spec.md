## ADDED Requirements

### Requirement: Calificacion model

The system SHALL maintain a `Calificacion` record per student per activity per materia. Each record SHALL store a numeric grade (`nota_numerica`, nullable), a textual grade (`nota_textual`, nullable), a derived `aprobado` boolean, and an origin enum (`Importado | Manual`). The `aprobado` field SHALL be derived at write time: if `nota_numerica` is present, compare against the materia's threshold percentage (from `UmbralMateria`); if only `nota_textual` is present, compare against the configured passing values. Each record SHALL reference an `EntradaPadron` and a `Materia`. Soft delete SHALL apply.

#### Scenario: Create numeric grade with aprobado=true
- **WHEN** a `Calificacion` is created with `nota_numerica=75` and the configured threshold for that materia is 60
- **THEN** `aprobado` is `true`

#### Scenario: Create numeric grade with aprobado=false
- **WHEN** a `Calificacion` is created with `nota_numerica=45` and the configured threshold for that materia is 60
- **THEN** `aprobado` is `false`

#### Scenario: Create textual grade with aprobado=true
- **WHEN** a `Calificacion` is created with `nota_textual="Satisfactorio"` and that value is in the configured passing values set
- **THEN** `aprobado` is `true`

#### Scenario: Create textual grade with aprobado=false
- **WHEN** a `Calificacion` is created with `nota_textual="No satisfactorio"` and that value is NOT in the configured passing values set
- **THEN** `aprobado` is `false`

#### Scenario: Default threshold when no UmbralMateria configured
- **WHEN** a `Calificacion` is created with `nota_numerica=55` and no `UmbralMateria` exists for the materia
- **THEN** `aprobado` is `false` (default threshold is 60)

#### Scenario: Soft delete preserves record
- **WHEN** a `Calificacion` is deleted through its repository
- **THEN** the record remains in the database with `deleted_at` populated

### Requirement: UmbralMateria model

The system SHALL allow configuring a passing threshold per `(asignacion_id, materia_id)` combination. Each `UmbralMateria` SHALL have `umbral_pct` (integer, default 60) and `valores_aprobatorios` (list of text values defining which textual grades count as passing). The threshold SHALL only apply to the data of the teacher assigned in that `asignacion_id` and SHALL NOT affect other teachers' data.

#### Scenario: Create UmbralMateria with custom threshold
- **WHEN** a user creates an `UmbralMateria` with `umbral_pct=70` for their assignment
- **THEN** the record is persisted with the custom threshold

#### Scenario: Create UmbralMateria with custom passing values
- **WHEN** a user creates an `UmbralMateria` with `valores_aprobatorios=["Aprobado", "Muy bueno"]` for their assignment
- **THEN** only those textual values count as passing for that teacher's data

#### Scenario: Threshold is isolated per assignment
- **WHEN** teacher A sets umbral_pct=75 and teacher B has no UmbralMateria for the same materia
- **THEN** teacher A's grades use the 75 threshold and teacher B's grades use the default 60

### Requirement: Import grades from LMS file with preview

The system SHALL provide a two-step import flow for grade files: (1) preview and (2) confirm. Step 1 SHALL accept an `.xlsx` or `.csv` file, parse it, detect numeric activity columns (header ending in `(Real)`, per RN-01), detect textual activity columns (non-numeric headers, per RN-02), match student rows against the active `VersionPadron` entries for the materia, and return a preview with detected activities, sample rows, and total count. Step 2 SHALL accept a preview token (or activity selection) to confirm and persist the `Calificacion` records.

#### Scenario: Successful preview detects numeric and textual columns
- **WHEN** a user uploads a valid `.xlsx` file with columns `[Nombre, Apellidos, TP1 (Real), TP2 (Real)]`
- **THEN** the system returns a preview with 2 detected numeric activities (`TP1`, `TP2`) and 0 textual activities

#### Scenario: Preview detects mixed columns
- **WHEN** a user uploads a valid `.xlsx` file with columns `[Nombre, Apellidos, TP1 (Real), Trabajo Final]`
- **THEN** the system returns a preview with 1 numeric activity (`TP1`) and 1 textual activity (`Trabajo Final`)

#### Scenario: Confirm import persists calificaciones
- **WHEN** a user confirms the import with selected activities
- **THEN** `Calificacion` records are created for each student × activity, with `origen=Importado` and `aprobado` derived

#### Scenario: Students are matched against active padron
- **WHEN** importing grades for a materia
- **THEN** each row is matched against `EntradaPadron` entries from the active `VersionPadron` for that `(materia, cohorte)`

#### Scenario: Unmatched rows are reported
- **WHEN** a student row in the file does not match any `EntradaPadron` entry
- **THEN** the system lists the unmatched rows separately and does NOT create `Calificacion` records for them

#### Scenario: Malformed file returns descriptive error
- **WHEN** a user uploads a malformed file without detectable student columns
- **THEN** the system returns 422 with details about the issue

### Requirement: Import completion report

The system SHALL accept a completion report file from the LMS and detect activities that are marked as submitted by the student but have no corresponding `Calificacion` record. This detection SHALL only apply to textual-scale activities (RN-08). The output SHALL be a list of potential ungraded assignments per student and activity.

#### Scenario: Detect ungraded textual activity
- **WHEN** a user uploads a completion report showing student X submitted "Trabajo Final" but there is no `Calificacion` with `actividad="Trabajo Final"` for that student
- **THEN** the system includes student X's "Trabajo Final" in the ungraded list

#### Scenario: Completed numeric activity is NOT reported
- **WHEN** a completion report shows student X submitted "TP1 (Real)" without a grade
- **THEN** the system does NOT include "TP1" in the ungraded list (per RN-08, numeric activities without a grade = not submitted)

#### Scenario: Graded activity is NOT reported
- **WHEN** student X has an existing `Calificacion` for "Trabajo Final" and the completion report shows it as submitted
- **THEN** the activity is NOT included in the ungraded list

### Requirement: Configure threshold per subject

The system SHALL allow a teacher to view and update their `UmbralMateria` for a given materia. When no `UmbralMateria` exists, the system SHALL return the default values (`umbral_pct=60`, `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`).

#### Scenario: Teacher reads current threshold
- **WHEN** a teacher requests the threshold for their materia
- **THEN** the system returns the existing `UmbralMateria` or the default values if none exists

#### Scenario: Teacher updates threshold
- **WHEN** a teacher updates `umbral_pct` from 60 to 75 for their materia
- **THEN** the `UmbralMateria` is updated and subsequent `aprobado` derivations use the new threshold

### Requirement: Audit trail

Every grade import operation SHALL generate an audit log entry with code `CALIFICACIONES_IMPORTAR`, recording actor ID, materia ID, activity names, and record count.

#### Scenario: Import generates audit entry
- **WHEN** a grade import is confirmed
- **THEN** an audit log entry is created with action `CALIFICACIONES_IMPORTAR`, including actor, materia, selected activities, and count of calificaciones created

### Requirement: Tenant isolation

All calificacion and umbral data SHALL be isolated by tenant. A query for grades in tenant A SHALL NOT return data from tenant B.

#### Scenario: Tenant isolation on query
- **WHEN** querying calificaciones for a materia in tenant A
- **THEN** only calificaciones belonging to tenant A are returned, even if tenant B has grades for the same materia UUID

#### Scenario: Cross-tenant umbral is not visible
- **WHEN** a teacher from tenant A queries threshold configuration for a materia
- **THEN** only tenant A's `UmbralMateria` records are visible
