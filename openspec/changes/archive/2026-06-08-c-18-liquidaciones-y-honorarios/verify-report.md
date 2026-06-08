## Verification Report: c-18-liquidaciones-y-honorarios

**Date**: 2026-06-08
**Tasks**: 36/36 complete

### Test Results

- Requested command `docker compose run --rm backend ...` could not run in this environment: Docker treated `compose` as an unavailable plugin and failed with `unknown flag: --rm`.
- Equivalent `docker-compose run --rm backend ...` also could not run because `docker-compose.yml` defines service `api`, not `backend`.
- First `docker-compose run --rm api ...` attempt could not start the compose `postgres` service because host port `5432` was already in use.
- A run against an already-running shared PostgreSQL test container reached pytest but failed with `DeadlockDetectedError` during `DROP SCHEMA public CASCADE`, consistent with concurrent/shared DB use.
- Final C-18 suite was run with an isolated temporary PostgreSQL 16 container on the project Docker network and the `api` service with `--no-deps`:
  - `40 passed, 1 warning in 91.74s (0:01:31)`
- Full safety suite was run with an isolated temporary PostgreSQL 16 container on the project Docker network and the `api` service with `--no-deps`:
  - `14 failed, 498 passed, 14 skipped, 2 warnings, 23 errors in 1140.87s (0:19:00)`
  - Failures/errors are outside the C-18 targeted files and include `tests/test_analisis.py`, `tests/test_coloquios.py`, `tests/test_comunicaciones.py`, `tests/test_encuentros.py`, `tests/test_migrations_tenancy.py`, and `tests/test_padron.py`.

### Spec Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Grilla salarial: salario base por rol, tenant y vigencia sin solapamientos | PASS | Models, migration indexes, repository lookups and service overlap validation are implemented; targeted tests passed. |
| Grilla salarial: Plus por grupo y rol tenant-scoped | PASS | `SalarioPlus` is tenant-scoped with vigencia lookups and overlap checks; API guarded by `LIQUIDACIONES_OPERAR_GRILLA`. |
| Grilla salarial: Materia to Plus mapping with cross-tenant validation | PASS | `MateriaPlus` is tenant-scoped; service validates materia via tenant-scoped context repository. |
| Liquidaciones: preview uses active assignments, active base, Materia to Plus and accumulated Plus per commission | PASS | `LiquidacionService.preview()` computes base plus `plus.monto * commission_count`; missing materia mapping contributes zero. |
| Liquidaciones: segment general, nexo and facturante | PASS | `SegmentoLiquidacion` exists; repository filters `general`, `nexo`, `facturante`; facturante wins when both flags are true. |
| Liquidaciones: facturantes excluded from payable total | PASS | Preview marks `excluido_por_factura=usuario.facturador` and excludes those items from `total_pagable`. |
| Liquidaciones: NEXO visible separately and included in payable summary | PASS | NEXO items set `es_nexo=True`; `total_pagable` includes non-facturante NEXO and `segmento_nexo_total` is exposed. |
| Liquidaciones: immutable close snapshot and duplicate close rejection | PASS | Close persists `EstadoLiquidacion.CERRADA` snapshots and rejects already closed cohort-periods; unique closed index exists. |
| Liquidaciones: history/detail filters by tenant, period, user and segment | PASS | `list_filtered()` scopes by `tenant_id` and supports period/cohort/user/state/segment; `get()` uses tenant-scoped base repository. |
| Liquidaciones API protection and close audit | PASS | Router uses `CurrentUserDep`, `require_permission(LIQUIDACIONES_CALCULAR_CERRAR)`, tenant from JWT and writes `LIQUIDACION_CERRAR`. |
| Facturas: register only for facturante users and keep opaque file reference | PASS | `FacturaService.register_factura()` rejects non-facturantes and persists `referencia_archivo` as an uninterpreted string. |
| Facturas: Pendiente to Abonada only | PASS | `mark_abonada()` only allows `EstadoFactura.PENDIENTE` and sets `abonada_at`. |
| Facturas: list filters and soft delete | PASS | Repository filters by user/period/status/date range and excludes `deleted_at` records. |
| Facturas API protection and extra-forbid payloads | PASS | Router uses `require_permission(FACTURAS_GESTIONAR)`; schemas use `ConfigDict(extra="forbid")` and do not accept client-controlled `tenant_id`. |

### Design Coherence

- Total = Base(rol vigente) + Sum(Plus(clave, rol) x comisiones_activas): FOLLOWED. Implemented in `LiquidacionService.preview()` via vigente repositories and `_commission_count()`.
- Snapshot persisted at close and immutable after close: FOLLOWED. `create_snapshot()` stores amounts, commissions, role and flags as closed records; later grid changes do not mutate snapshots.
- Segment filter `general|nexo|facturante`; facturante wins when both flags true: FOLLOWED. `list_filtered()` prioritizes `FACTURANTE` by `excluido_por_factura`, then `NEXO`, then `GENERAL`.
- Tenant isolation via `tenant_id` and repository filters: FOLLOWED for C-18. Repositories are tenant-scoped and context queries include tenant filters.
- RBAC permissions `LIQUIDACIONES_OPERAR_GRILLA`, `LIQUIDACIONES_CALCULAR_CERRAR`, `FACTURAS_GESTIONAR`: FOLLOWED. Routers use constants with `require_permission(...)`.
- Soft delete: FOLLOWED. C-18 list/get paths use tenant-scoped repositories and delete operations route through `soft_delete()`.
- Pydantic `extra='forbid'`: FOLLOWED. C-18 schemas define `ConfigDict(extra="forbid")`.
- No business logic in routers: FOLLOWED for C-18. Routers delegate to services and map service errors to HTTP responses.
- No direct DB access in services: FOLLOWED for C-18. Services instantiate repositories and do not execute SQL directly.

### Summary

- CRITICAL: None found in C-18 implementation. Targeted C-18 suite passes against isolated real PostgreSQL.
- WARNING: The exact requested Docker command cannot run as written in this repo/environment because Compose service is `api`, not `backend`, and `docker compose` plugin is unavailable; verification used `docker-compose run --no-deps api` with an isolated PostgreSQL container.
- WARNING: The full `tests/` safety suite is not green: `14 failed, 23 errors`. The observed failures are outside C-18 targeted files and appear in older/non-C18 suites.
- SUGGESTION: Normalize test orchestration docs/commands to the current compose service name (`api`) and isolate PostgreSQL test DBs to avoid port conflicts and schema-drop deadlocks.

**Verdict**: READY FOR ARCHIVE
