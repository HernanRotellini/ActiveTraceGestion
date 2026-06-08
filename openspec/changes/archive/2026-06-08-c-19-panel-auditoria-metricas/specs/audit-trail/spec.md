# audit-trail Specification — Delta

## MODIFIED Requirements

### Requirement: Audit log query
The system SHALL allow authorized users (with `auditoria:ver` permission) to query the audit log filtered by tenant, date range, actor, action code, and materia. Users with COORDINADOR role SHALL only see entries for their own assigned materias (scope `(propio)`).

#### Scenario: Query filtered by date range (unchanged)
- **WHEN** a user with `auditoria:ver` queries entries between two dates
- **THEN** only entries within that range are returned

#### Scenario: Query filtered by actor (unchanged)
- **WHEN** a user with `auditoria:ver` queries entries for a specific actor
- **THEN** only entries by that actor are returned

#### Scenario: Tenant isolation in query (unchanged)
- **WHEN** a user queries the audit log
- **THEN** only entries from their own tenant are returned

#### Scenario: COORDINADOR sees only own materias (ADDED)
- **WHEN** a user with COORDINADOR role queries the audit log
- **THEN** only entries for materias where the user has asignaciones with COORDINADOR role are returned

#### Scenario: ADMIN sees all entries (ADDED)
- **WHEN** a user with ADMIN role queries the audit log
- **THEN** all entries within the tenant are returned without materia scope restriction
