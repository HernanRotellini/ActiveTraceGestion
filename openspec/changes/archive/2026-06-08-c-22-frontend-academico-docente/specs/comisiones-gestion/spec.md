## ADDED Requirements

### Requirement: Importar calificaciones con preview y selección
The system SHALL provide a UI for PROFESOR to import grades from an LMS file, preview detected activities, and select which activities to include.

#### Scenario: Upload file and see preview
- **WHEN** the user uploads a valid grades file for a selected subject
- **THEN** the system displays a preview table with detected activities (name, type) and checkboxes to select them

#### Scenario: Select activities and confirm import
- **WHEN** the user checks specific activities and clicks confirm
- **THEN** the system POSTs to `/api/admin/materias/{id}/calificaciones/importar` and shows a success notification with count of imported records

#### Scenario: Invalid file shows error
- **WHEN** the user uploads a malformed or unreadable file
- **THEN** the system shows a descriptive error message and does not proceed to preview

### Requirement: Configurar umbral de aprobación
The system SHALL allow the PROFESOR to view and set the passing threshold percentage per subject.

#### Scenario: View current threshold
- **WHEN** the user opens the threshold configuration for a subject
- **THEN** the system displays the current threshold value (default 60%)

#### Scenario: Update threshold
- **WHEN** the user enters a new percentage value and saves
- **THEN** the system PUTs to `/api/admin/materias/{id}/umbral` and shows a success confirmation

#### Scenario: Invalid threshold value rejected
- **WHEN** the user enters a value outside 0-100 range
- **THEN** the form validation shows an inline error and does not submit

### Requirement: Visualizar alumnos atrasados
The system SHALL display a table of students who are behind (missing activities or below threshold) for the selected subject.

#### Scenario: Atrasados table loads
- **WHEN** the user navigates to the atrasados view for a subject
- **THEN** the system fetches from `GET /api/v1/analisis/materias/{id}/atrasados` and renders a table with student name, missing activities count, and grade status

#### Scenario: Empty state
- **WHEN** no students are atrasados
- **THEN** the system shows an empty state message: "No hay alumnos atrasados"

### Requirement: Ranking de actividades aprobadas
The system SHALL display a ranking of students ordered by number of approved activities.

#### Scenario: Ranking table loads
- **WHEN** the user opens the ranking view
- **THEN** the system fetches from `GET /api/v1/analisis/materias/{id}/ranking` and renders an ordered table with student name and approved count

#### Scenario: Ranking excludes students with zero approved
- **WHEN** a student has zero approved activities
- **THEN** that student does NOT appear in the ranking (per RN-09)

### Requirement: Notas finales agrupadas
The system SHALL display grouped final grades per student based on selected activities.

#### Scenario: Notas finales table loads
- **WHEN** the user opens the notas finales view
- **THEN** the system fetches from `GET /api/v1/analisis/materias/{id}/notas-finales` and renders a table grouped by student with computed grade

### Requirement: Reportes rápidos
The system SHALL show a consolidated metrics dashboard for the selected subject.

#### Scenario: Reportes view shows KPIs
- **WHEN** the user views reportes rápidos for a subject
- **THEN** the system displays consolidated metrics: total students, approved count, atrasados count, average grade

#### Scenario: No data state
- **WHEN** no data has been imported yet
- **THEN** the system shows an informative state message indicating there is no data yet
