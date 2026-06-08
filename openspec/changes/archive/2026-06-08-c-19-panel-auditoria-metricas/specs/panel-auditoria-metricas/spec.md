# panel-auditoria-metricas Specification

## Purpose
Provide aggregated views over the audit log for supervision, operational monitoring, and regulatory compliance. The panel exposes read-only metrics that let COORDINADOR, ADMIN, and FINANZAS understand system usage patterns, detect inactive instructors, and investigate communication issues.

## ADDED Requirements

### Requirement: Actions per day timeline
The system SHALL expose a time-series aggregation of audit log entries grouped by day, filtered by date range and optional materia.

#### Scenario: Actions per day within date range
- **WHEN** a user with `auditoria:ver` queries actions per day with a date range
- **THEN** the system returns a list of `{fecha: date, total: int}` entries sorted chronologically

#### Scenario: Actions per day filtered by materia
- **WHEN** a user with `auditoria:ver` queries actions per day with a materia_id filter
- **THEN** only entries for that materia are included in the aggregation

#### Scenario: Empty date range returns zero entries
- **WHEN** a user queries actions per day for a date range with no audit entries
- **THEN** the system returns an empty list

### Requirement: Communications status by instructor
The system SHALL expose the distribution of communication states (Pendiente, Enviando, Enviado, Fallido, Cancelado) grouped by instructor and optionally by materia.

#### Scenario: Communication states grouped by instructor
- **WHEN** a user with `auditoria:ver` queries communication status by instructor
- **THEN** the system returns a list of `{docente_id: UUID, docente_nombre: str, pendiente: int, enviando: int, enviado: int, fallido: int, cancelado: int}`

#### Scenario: Filtered by materia
- **WHEN** a user queries communication status with a materia_id filter
- **THEN** only communications for that materia are included

#### Scenario: Instructor with no communications
- **WHEN** an instructor has no communication entries in the period
- **THEN** they are not included in the result set

### Requirement: Interactions by instructor and materia
The system SHALL expose a breakdown of action types (previsualización, importación, envío, reset, umbral, envíos exitosos, fallidos, batches) grouped by instructor and materia.

#### Scenario: Interactions grouped by instructor and materia
- **WHEN** a user with `auditoria:ver` queries interactions by instructor and materia
- **THEN** the system returns a list of `{docente_id: UUID, materia_id: UUID, materia_nombre: str, accion: str, total: int}` entries

#### Scenario: Filtered by date range
- **WHEN** a user queries interactions with a date range filter
- **THEN** only entries within that range are included

#### Scenario: Filtered by instructor
- **WHEN** a user queries interactions with an actor_id filter
- **THEN** only entries for that instructor are included

### Requirement: Recent actions log
The system SHALL expose the most recent audit log entries with a configurable maximum limit (default 200, max 1000), including full entry details.

#### Scenario: Recent actions with default limit
- **WHEN** a user with `auditoria:ver` queries recent actions without specifying limit
- **THEN** the system returns up to 200 most recent entries

#### Scenario: Recent actions with custom limit
- **WHEN** a user queries recent actions with `max_results=50`
- **THEN** the system returns up to 50 most recent entries

#### Scenario: Limit is capped at maximum
- **WHEN** a user queries recent actions with `max_results=5000`
- **THEN** the system returns at most 1000 entries (the configured maximum)

### Requirement: Scope (propio) for COORDINADOR
The system SHALL restrict panel results to the COORDINADOR's own assigned materias when the requesting user has the COORDINADOR role. ADMIN and FINANZAS see all data without restriction.

#### Scenario: COORDINADOR sees only own materias
- **WHEN** a user with COORDINADOR role queries any panel endpoint
- **THEN** results are filtered to materias where the user has asignaciones with COORDINADOR role

#### Scenario: ADMIN sees all data
- **WHEN** a user with ADMIN role queries any panel endpoint
- **THEN** no materia scope filter is applied

#### Scenario: FINANZAS sees all data
- **WHEN** a user with FINANZAS role queries any panel endpoint
- **THEN** no materia scope filter is applied
