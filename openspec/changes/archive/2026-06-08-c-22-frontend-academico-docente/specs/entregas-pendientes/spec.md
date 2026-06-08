## ADDED Requirements

### Requirement: Detectar entregas sin corregir
The system SHALL allow the PROFESOR to detect submissions that are completed by students but not yet graded, by uploading an LMS completion report.

#### Scenario: Upload completion report
- **WHEN** the user uploads an LMS completion report for a subject
- **THEN** the system processes it and displays a table of potential ungraded submissions, grouped by activity and student name

#### Scenario: Only textual-scale activities included
- **WHEN** the report is processed
- **THEN** only activities with textual grading scales are included in the results (per RN-08); numeric-scale activities are excluded

#### Scenario: No pending submissions
- **WHEN** all submissions have been graded
- **THEN** the system shows "No hay entregas pendientes de corrección"

### Requirement: Exportar entregas sin corregir
The system SHALL allow the PROFESOR to download the list of ungraded submissions as a file.

#### Scenario: Export as CSV
- **WHEN** the user clicks the export button
- **THEN** the system downloads a CSV file with columns: student name, activity name, submission date

#### Scenario: Export disabled when no data
- **WHEN** there are no pending submissions
- **THEN** the export button is disabled with a tooltip explaining why
