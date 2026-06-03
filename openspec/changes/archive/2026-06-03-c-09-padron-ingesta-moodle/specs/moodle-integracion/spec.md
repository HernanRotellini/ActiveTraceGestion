## ADDED Requirements

### Requirement: Moodle Web Services client
The system SHALL provide a `MoodleClient` class in `integrations/moodle_ws.py` that communicates with Moodle via its Web Services API using httpx async. The client SHALL support at least: sync enrolled users for a course, sync activities for a course. The client SHALL be configurable per tenant (base URL + token).

#### Scenario: Sync users from Moodle course
- **WHEN** the system calls `MoodleClient.sync_usuarios(materia_id)` for a materia with a valid Moodle course mapping
- **THEN** the client fetches enrolled users from Moodle and returns normalized user data (nombre, apellidos, email)

#### Scenario: Moodle WS unavailable returns 502
- **WHEN** the Moodle server is unreachable during a sync call
- **THEN** the system returns a 502 Bad Gateway response and the caller can fall back to manual import

### Requirement: Sync on-demand
The system SHALL expose `POST /api/moodle/sync/{materia_id}` to trigger an on-demand sync. Only PROFESOR (own materia) and COORDINADOR (global) SHALL be authorized.

#### Scenario: Teacher triggers on-demand sync
- **WHEN** a teacher calls POST /api/moodle/sync/{materia_id} for their materia
- **THEN** the system performs a sync via MoodleClient and imports the results as a new padron version

#### Scenario: Unauthorized user cannot sync
- **WHEN** a user without `padron:importar` permission calls POST /api/moodle/sync/{materia_id}
- **THEN** the system returns 403 Forbidden

### Requirement: Scheduled nightly sync
The system SHALL support a scheduled nightly sync (configurable via cron/scheduler) that processes all tenants and materias with Moodle integration enabled.

#### Scenario: Nightly sync processes all configured materias
- **WHEN** the nightly sync job runs
- **THEN** the system iterates over all materias with active Moodle configuration per tenant and triggers sync

### Requirement: Fallback to manual import
When Moodle Web Services are not configured for a tenant, the system SHALL allow importing padron data exclusively via file upload (xlsx/csv). The `MoodleClient` SHALL be optional: the padron service SHALL degrade gracefully when Moodle credentials are absent.

#### Scenario: No Moodle config, manual import works
- **WHEN** a tenant has no Moodle credentials configured
- **THEN** the sync endpoint returns 400 with a message indicating Moodle is not configured, and the manual import endpoint works normally

### Requirement: Sync error handling with retry
The Moodle client SHALL implement retry logic with exponential backoff (3 attempts) for transient network errors. Non-transient errors (auth failure, invalid course ID) SHALL fail immediately with a descriptive error.

#### Scenario: Transient error retries
- **WHEN** the Moodle server returns a 503 (transient) on first attempt
- **THEN** the client retries up to 2 more times with backoff before failing

#### Scenario: Auth failure is immediate
- **WHEN** the Moodle server returns 401 (invalid token)
- **THEN** the client fails immediately without retry
