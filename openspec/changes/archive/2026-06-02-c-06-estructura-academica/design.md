## Context

C-06 builds the foundational academic registry (Carrera, Cohorte, Materia) on top of the existing tenant-scoped infrastructure established in C-01 (database, TSM) and C-04 (RBAC with `estructura:gestionar` permission). The models follow the same patterns as the RBAC entities: `TenantScopedMixin`, UUID PK, soft delete, Pydantic v2 schemas with `extra='forbid'`, tenant-scoped repositories, and service layer with business rules.

## Goals / Non-Goals

**Goals:**

- Provide CRUD APIs for Carrera, Cohorte, and Materia under `/api/admin/`
- Enforce uniqueness: `(tenant_id, codigo)` for Carrera and Materia; `(tenant_id, carrera_id, nombre)` for Cohorte
- Prevent new cohorts on inactive carreras
- Full multi-tenant isolation (tenant A cannot see tenant B's data)
- Soft delete on all entities (audit trail)

**Non-Goals:**

- Dictado entity (the Materia-instance per carrera×cohorte is deferred to a future change — this change only builds the catalog)
- Frontend UI (API-only change)
- PII encryption (none of these entities carry sensitive PII)

## Decisions

1. **One service, three repositories** — a single `EstructuraAcademicaService` orchestrates all three CRUDs to keep the API surface cohesive; each entity gets its own repository for clean SQL isolation.
2. **Naming pattern** — repositories and models follow the existing RBAC pattern: `CarreraRepository(TenantScopedRepository[Carrera])`, `CohorteRepository`, `MateriaRepository`.
3. **Unique constraint at DB + service** — composite unique indexes in the migration enforce integrity at the database level; the service layer pre-checks before insert to return a clear 409 rather than a raw DB constraint violation.
4. **Inactive check as business rule** — when creating a cohort, the service checks `Carrera.estado == "activa"`; this is explicit rule logic, not a DB constraint (because the state may change over time).
5. **Pydantic Request/Response separation** — create/update request schemas use `extra='forbid'` but allow partial fields for update; response schemas include `id`, `created_at`, `updated_at` with `from_attributes=True`.
6. **No pagination in MVP** — the catalog is small (tens to low hundreds per tenant); list returns all records. Pagination can be added later if needed.

## Risks / Trade-offs

- [Risk] Cohorte creation depends on Carrera existence + active state → [Mitigation] service returns 404 if carrera not found, 409 if inactive
- [Risk] Soft-deleted records could cause confusion in list views → [Mitigation] repositories filter `deleted_at IS NULL` by default; admin endpoints could expose a `?incluir_eliminados` flag later
- [Risk] Codigo uniqueness without case normalization could cause "PROG_I" vs "prog_i" → [Trade-off] accepted for now; codigo is a business identifier the tenant controls
