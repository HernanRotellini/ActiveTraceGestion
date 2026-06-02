## Why

The academic management workflow requires a structured catalog of carreras, cohortes, and materias as the foundation for all downstream modules (calificaciones, equipos docentes, encuentros, liquidaciones). Without these entities, no course can be configured, no teacher can be assigned, and no student cohort can be tracked. C-06 builds the core academic registry — the backbone that all other academic features depend on.

## What Changes

- **New models**: `Carrera`, `Cohorte`, `Materia` with tenant-scoped soft delete, UUID PKs, and unique constraints per ADR-006
- **New migration 004**: creates `carreras`, `cohortes`, `materias` tables
- **New service layer**: `EstructuraAcademicaService` with CRUD + business rules (uniqueness, inactive check)
- **New REST endpoints**: `/api/admin/carreras`, `/api/admin/cohortes`, `/api/admin/materias` with full CRUD
- **New permission guard**: all endpoints protected by `estructura:gestionar` (ADMIN role)
- **Tests**: CRUD, uniqueness per tenant, multi-tenant isolation, active/inactive state transitions

## Capabilities

### New Capabilities
- `estructura-academica`: CRUD for Carrera, Cohorte, Materia with tenant isolation, unique constraints, and inactive-state business rules

### Modified Capabilities
- (none — first academic domain capability)

## Impact

- **Backend**: new models/ `carrera.py`, `cohorte.py`, `materia.py`; new schemas/ `estructura_academica.py`; new repositories/ `estructura_academica.py`; new services/ `estructura_academica.py`; new router `api/v1/routers/estructura_academica.py`; wire into app routers
- **Database**: migration 004 with 3 new tables and unique composite indexes
- **Tests**: new suite `tests/test_estructura_academica.py`
