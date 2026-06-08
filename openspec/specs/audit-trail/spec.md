# audit-trail Specification

## Purpose
Provide an immutable, append-only record of all significant actions performed in the system, including actions taken under impersonation. The audit trail is the source of truth for compliance, security review, and operational forensics.

## Requirements

### Requirement: Append-only audit log
The system SHALL maintain an `audit_log` table where entries can only be inserted — never updated or deleted — at both application and database level.

#### Scenario: Insert is allowed
- **WHEN** a significant action is completed
- **THEN** a new audit entry is inserted with all required fields

#### Scenario: Update is rejected
- **WHEN** an UPDATE statement targets the `audit_log` table
- **THEN** the database rejects the operation with an error

#### Scenario: Delete is rejected
- **WHEN** a DELETE statement targets the `audit_log` table
- **THEN** the database rejects the operation with an error

### Requirement: Audit entry structure
Each audit entry SHALL contain: actor_id (who performed), impersonado_id (who was impersonated, nullable), tenant_id, materia_id (nullable), accion (standardized code), detalle (JSON context), filas_afectadas (integer count), ip, user_agent, and fecha_hora.

#### Scenario: Full audit entry on action
- **WHEN** a significant action is logged
- **THEN** the entry includes actor_id, tenant_id, accion code, fecha_hora, ip, and user_agent
- **AND** detalle contains relevant JSON context
- **AND** filas_afectadas reflects the number of affected records

#### Scenario: Impersonation includes both identities
- **WHEN** an action is performed under impersonation
- **THEN** actor_id is the impersonator (real user) and impersonado_id is the impersonated user

#### Scenario: Materia is optional
- **WHEN** the action is not related to a specific materia
- **THEN** materia_id is NULL

### Requirement: Action code catalog
The system SHALL provide a standardized catalog of action codes for logging significant operations.

#### Scenario: Import action codes exist
- **WHEN** the system imports data
- **THEN** codes CALIFICACIONES_IMPORTAR and PADRON_CARGAR are available

#### Scenario: Communication action codes exist
- **WHEN** communication actions occur
- **THEN** codes COMUNICACION_ENVIAR, COMUNICACION_APROBAR, COMUNICACION_CANCELAR are available

#### Scenario: Assignment and financial action codes exist
- **WHEN** assignment or financial actions occur
- **THEN** codes ASIGNACION_MODIFICAR, LIQUIDACION_CERRAR are available

#### Scenario: Impersonation action codes exist
- **WHEN** impersonation starts or ends
- **THEN** codes IMPERSONACION_INICIAR and IMPERSONACION_FINALIZAR are available

### Requirement: Impersonation tracking
The system SHALL distinguish impersonated sessions from normal sessions and record audit entries with the real actor identity.

#### Scenario: Impersonation start is logged
- **WHEN** a user with `impersonacion:usar` permission starts impersonating another user
- **THEN** an audit entry with code IMPERSONACION_INICIAR is created
- **AND** actor_id is the impersonator and impersonado_id is the target

#### Scenario: Impersonation end is logged
- **WHEN** an impersonation session ends
- **THEN** an audit entry with code IMPERSONACION_FINALIZAR is created

#### Scenario: Actions under impersonation are attributed to real actor
- **WHEN** an impersonated user performs an action
- **THEN** the audit entry's actor_id is the impersonator (NOT the impersonated user)
- **AND** impersonado_id records who was being impersonated

### Requirement: Audit log query
The system SHALL allow authorized users (with `auditoria:ver` permission) to query the audit log filtered by tenant, date range, actor, action code, and materia. Users with COORDINADOR role SHALL only see entries for their own assigned materias (scope `(propio)`).

#### Scenario: Query filtered by date range
- **WHEN** a user with `auditoria:ver` queries entries between two dates
- **THEN** only entries within that range are returned

#### Scenario: Query filtered by actor
- **WHEN** a user with `auditoria:ver` queries entries for a specific actor
- **THEN** only entries by that actor are returned

#### Scenario: Tenant isolation in query
- **WHEN** a user queries the audit log
- **THEN** only entries from their own tenant are returned

#### Scenario: COORDINADOR sees only own materias
- **WHEN** a user with COORDINADOR role queries the audit log
- **THEN** only entries for materias where the user has asignaciones with COORDINADOR role are returned

#### Scenario: ADMIN sees all entries
- **WHEN** a user with ADMIN role queries the audit log
- **THEN** all entries within the tenant are returned without materia scope restriction
