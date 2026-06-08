## ADDED Requirements

### Requirement: Monitor de seguimiento filtrable
The system SHALL provide a filterable view of students' activity status for TUTOR and PROFESOR roles.

#### Scenario: Monitor loads with default filters
- **WHEN** the user opens the monitor view
- **THEN** the system shows a filter panel with fields: student name, email, comisión, regional, activity, minimum approved count; and a results table beneath it

#### Scenario: Apply filters and see results
- **WHEN** the user selects filter values and clicks "apply"
- **THEN** the system fetches filtered data and renders the results table with columns: student name, email, comisión, approved count, missing count, status indicator

#### Scenario: Clear filters resets to default
- **WHEN** the user clicks "clear" or "limpiar"
- **THEN** all filter fields reset to their default values and the table shows unfiltered results

#### Scenario: Empty results
- **WHEN** no students match the applied filters
- **THEN** the system shows "No se encontraron alumnos con los filtros seleccionados"

#### Scenario: Export filtered results
- **WHEN** the user clicks export
- **THEN** the system downloads a CSV file with the currently filtered results
