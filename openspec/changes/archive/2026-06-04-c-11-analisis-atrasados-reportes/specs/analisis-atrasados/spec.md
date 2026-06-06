## ADDED Requirements

### Requirement: Cómputo de alumnos atrasados (F2.2, RN-06)

The system SHALL compute the list of students with delayed status for a given materia, based on the active `VersionPadron` entries and their corresponding `Calificacion` records. A student SHALL be considered "atrasado" if they have at least one activity with no `Calificacion` record (faltante) OR at least one activity where `aprobado = false` (nota inferior al umbral configurado per RN-03). The computation SHALL only consider activities that have been imported for the materia. The result SHALL include per-student detail of which specific activities are atrasadas and why (faltante vs nota insuficiente).

#### Scenario: Student is atrasado due to missing activity
- **WHEN** a student has no `Calificacion` record for activity "TP1" in the materia
- **THEN** the student SHALL appear in the atrasados list with activity "TP1" marked as "faltante"

#### Scenario: Student is atrasado due to insufficient grade
- **WHEN** a student has a `Calificacion` for activity "TP1" with `nota_numerica=40` and the configured threshold is 60
- **THEN** the student SHALL appear in the atrasados list with activity "TP1" marked as "nota insuficiente"

#### Scenario: Student with all activities approved is NOT atrasado
- **WHEN** a student has `Calificacion` records for all detected activities and all have `aprobado = true`
- **THEN** the student SHALL NOT appear in the atrasados list

#### Scenario: No activities imported for materia
- **WHEN** the materia has no `Calificacion` records at all
- **THEN** the system SHALL return an empty atrasados list with an informational status indicating no data

#### Scenario: Student in active padron but no usuario_id
- **WHEN** an `EntradaPadron` entry exists with `usuario_id = NULL` (student without account) and the student has no calificaciones
- **THEN** the student SHALL appear in the atrasados list using their name/apellidos from the padron entry

#### Scenario: Scope isolation by materia
- **WHEN** querying atrasados for materia A
- **THEN** only students from materia A's active padron are evaluated; materia B data is excluded

### Requirement: Ranking de actividades aprobadas (F2.3, RN-09)

The system SHALL return an ordered ranking of students by count of approved activities for a given materia. The ranking SHALL exclude students with zero approved activities (RN-09). The result SHALL be sorted descending by approval count. In case of tie, SHALL sort alphabetically by student surname and name.

#### Scenario: Ranking with multiple students
- **WHEN** student A has 4 approved activities, student B has 2, student C has 0
- **THEN** the ranking returns A (1st, 4), B (2nd, 2); C is excluded

#### Scenario: Ranking with tie
- **WHEN** student A has 3 approved activities and student B has 3 approved activities
- **THEN** both appear in order by surname and name alphabetically

#### Scenario: Ranking with no approved activities
- **WHEN** no student has any approved activity in the materia
- **THEN** the system returns an empty ranking

#### Scenario: Ranking is filtered by materia
- **WHEN** querying ranking for materia A
- **THEN** only students from materia A's active padron are included

### Requirement: Reportes rápidos por materia (F2.4)

The system SHALL return a consolidated metrics view for a materia, including: total enrolled students, total detected activities, count of atrasados students, count of students with all activities approved, approval rate percentage (students with at least one approved / total enrolled), and per-activity approval statistics (total submitted, approved count, approval rate).

#### Scenario: Report with complete data
- **WHEN** a materia has 30 enrolled students, 5 activities, 8 atrasados, 22 with at least one approval
- **THEN** the system returns: total_alumnos=30, total_actividades=5, atrasados=8, con_aprobadas=22, tasa_aprobacion=73.33

#### Scenario: Report with no data
- **WHEN** a materia has no calificaciones imported
- **THEN** the system returns a report with zero counts and an informational status

#### Scenario: Per-activity breakdown
- **WHEN** a materia has activity "TP1" with 30 submissions and 20 approved
- **THEN** the report includes per-activity entry for "TP1" with total=30, aprobados=20, tasa=66.67

### Requirement: Notas finales agrupadas (F2.5)

The system SHALL compute a final grade per student for a given materia, based on a provided list of activity names to include. The final grade SHALL be the average of `nota_numerica` values for those activities. If a student has no `nota_numerica` for an activity (only `nota_textual`), that activity SHALL be excluded from the average for that student. The system SHALL also derive an `aprobado` boolean for the final grade, comparing the average against the materia's configured threshold. Activities not in the provided list SHALL be ignored.

#### Scenario: Final grade with all numeric activities
- **WHEN** activities ["TP1", "TP2", "TP3"] are selected, and student A has notas 70, 80, 90 respectively
- **THEN** the final grade is 80.0 with `aprobado = true` (threshold 60)

#### Scenario: Final grade below threshold
- **WHEN** activities ["TP1", "TP2"] are selected, and student A has notas 40, 50 respectively
- **THEN** the final grade is 45.0 with `aprobado = false` (threshold 60)

#### Scenario: Student missing some selected activities
- **WHEN** activities ["TP1", "TP2", "TP3"] are selected, and student A only has notas for "TP1" (70) and "TP3" (90)
- **THEN** the final grade is 80.0 (average of existing activities only)

#### Scenario: No selected activities match any calificacion
- **WHEN** the selected activity list is empty or contains no matching activity names
- **THEN** the system returns an empty result with an informational message

### Requirement: Exportar trabajos prácticos sin corregir (F2.6, RN-07, RN-08)

The system SHALL generate a downloadable file (CSV) listing potential ungraded assignments. The detection SHALL only include textual-scale activities (RN-08) that are marked as submitted in the LMS completion report but have no corresponding `Calificacion` record (RN-07). The export SHALL include columns: student name, student surname, activity name, comision, regional, materia name. The file SHALL use UTF-8 encoding with BOM for Excel compatibility.

#### Scenario: Export with ungraded textual assignments
- **WHEN** a student submitted "Trabajo Final" (textual activity) but has no `Calificacion` for it
- **THEN** the CSV includes one row for that student and activity

#### Scenario: Export excludes numeric activities
- **WHEN** a student submitted "TP1 (Real)" (numeric activity) without a grade
- **THEN** the CSV does NOT include that activity (per RN-08)

#### Scenario: Export excludes graded activities
- **WHEN** a student has an existing `Calificacion` for "Trabajo Final" with `origen=Importado`
- **THEN** the CSV does NOT include that student-activity pair

#### Scenario: Export with no ungraded assignments
- **WHEN** all submitted assignments have corresponding `Calificacion` records
- **THEN** the CSV contains only headers with no data rows

### Requirement: Monitor general de actividades (F2.7, COORDINADOR/ADMIN)

The system SHALL provide a transversal view of all students in the tenant with their activity status. The endpoint SHALL accept optional filters: `materia_id`, `regional`, `comision`, `busqueda` (free text by student name/surname/email), `actividad` (specific activity name), `min_actividad_cumplida` (minimum number of approved activities for a student to be included). The response SHALL include per-student detail: name, surname, regional, comision, activites summary (total, approved count, pending count), and atrasado status. The response SHALL be paginated.

#### Scenario: Monitor with materia filter
- **WHEN** a COORDINADOR queries the monitor with `materia_id=X`
- **THEN** only students from materia X's active padron are returned

#### Scenario: Monitor with text search
- **WHEN** a COORDINADOR queries the monitor with `busqueda="Pérez"`
- **THEN** only students whose name or surname contains "Pérez" are returned

#### Scenario: Monitor with minimum approved activities
- **WHEN** a COORDINADOR queries the monitor with `min_actividad_cumplida=3`
- **THEN** only students with 3 or more approved activities are included

#### Scenario: Monitor returns paginated
- **WHEN** a COORDINADOR queries the monitor with `page=1&per_page=20`
- **THEN** the response includes `data`, `total`, `page`, `per_page`, `total_pages`

#### Scenario: Monitor empty result with filters
- **WHEN** no students match the applied filters
- **THEN** the response returns an empty data array with `total=0`

### Requirement: Monitor de seguimiento por tutor/profesor (F2.8, TUTOR, PROFESOR)

The system SHALL provide a filtered view of activity status for students assigned to the authenticated user. The scope SHALL be automatically limited to the user's own asignaciones (materias where they have an active assignment with a role). The same filters and pagination as the general monitor SHALL apply, except the materia filter SHALL be pre-scoped to the user's own materias. TUTOR scope SHALL include all students in those materias (not further filtered). PROFESOR scope SHALL be the same.

#### Scenario: Tutor sees their assigned students
- **WHEN** a TUTOR queries their monitor
- **THEN** only students from materias where the TUTOR has active assignments are returned

#### Scenario: Professor sees their assigned students
- **WHEN** a PROFESOR queries their monitor
- **THEN** only students from materias where the PROFESOR has active assignments are returned

#### Scenario: User with no assignments
- **WHEN** a TUTOR has no active assignments in any materia
- **THEN** the monitor returns an empty result

#### Scenario: Tutor can filter within scope
- **WHEN** a TUTOR queries their monitor with `actividad="TP1"`
- **THEN** the result is filtered to students with activity "TP1" within the TUTOR's materias

### Requirement: Monitor de seguimiento con rango de fechas (F2.9, COORDINADOR/ADMIN)

The system SHALL extend the coordinator/admin monitor (F2.7) with additional `fecha_desde` and `fecha_hasta` filters. When provided, the system SHALL only consider `Calificacion` records whose `importado_at` falls within the specified date range. This SHALL affect all computed metrics (atrasados count, approval counts, rankings) within the monitor.

#### Scenario: Monitor with date range
- **WHEN** a COORDINADOR queries with `fecha_desde=2026-03-01&fecha_hasta=2026-03-31`
- **THEN** only calificaciones imported in March 2026 are considered for metrics

#### Scenario: Monitor with only fecha_desde
- **WHEN** a COORDINADOR queries with `fecha_desde=2026-03-01` and no `fecha_hasta`
- **THEN** all calificaciones imported from March 2026 onwards are considered

#### Scenario: Monitor with only fecha_hasta
- **WHEN** a COORDINADOR queries with `fecha_hasta=2026-03-31` and no `fecha_desde`
- **THEN** all calificaciones imported up to March 2026 are considered

### Requirement: Authorization and scope (atrasados:ver)

All endpoints under `/api/analisis/*` SHALL require the `atrasados:ver` permission. TUTOR and PROFESOR SHALL have scope `(propio)` — their queries SHALL be automatically scoped to their active asignaciones. COORDINADOR and ADMIN SHALL have scope global — they SHALL query across all materias in the tenant. Users without `atrasados:ver` SHALL receive 403 Forbidden. Unauthenticated requests SHALL receive 401 Unauthorized.

#### Scenario: Professor with atrasados:ver is authorized
- **WHEN** a PROFESOR with `atrasados:ver` requests a report for their own materia
- **THEN** the system returns 200 with the data

#### Scenario: User without atrasados:ver is denied
- **WHEN** a user without `atrasados:ver` requests any `/api/analisis/` endpoint
- **THEN** the system returns 403 Forbidden

#### Scenario: Unauthenticated request is denied
- **WHEN** an unauthenticated request hits `/api/analisis/`
- **THEN** the system returns 401 Unauthorized

#### Scenario: ALUMNO role does not have atrasados:ver
- **WHEN** an ALUMNO tries to access any `/api/analisis/` endpoint
- **THEN** the system returns 403 Forbidden

### Requirement: Tenant isolation

All analysis queries SHALL be isolated by tenant. A query for atrasados, ranking, or reports in tenant A SHALL NOT return data from tenant B.

#### Scenario: Tenant isolation on atrasados query
- **WHEN** querying atrasados for materia X in tenant A
- **THEN** only data from tenant A is returned, even if tenant B has the same materia UUID

#### Scenario: Tenant isolation on monitor
- **WHEN** an ADMIN from tenant A queries the general monitor
- **THEN** only tenant A's data is returned

### Requirement: Audit trail

Export operations (`GET /api/analisis/exportar-tps`) SHALL generate an audit log entry with action `ANALISIS_EXPORTAR`, recording actor ID, materia ID, and record count. Monitor queries MAY generate an audit entry with action `ANALISIS_CONSULTAR` for ADMIN-level queries.

#### Scenario: Export generates audit entry
- **WHEN** a user exports ungraded TPs for a materia
- **THEN** an audit log entry is created with action `ANALISIS_EXPORTAR`, including actor, materia, and count of rows exported

#### Scenario: Monitor query generates audit entry (admin)
- **WHEN** an ADMIN queries the general monitor
- **THEN** an audit log entry MAY be created with action `ANALISIS_CONSULTAR`
