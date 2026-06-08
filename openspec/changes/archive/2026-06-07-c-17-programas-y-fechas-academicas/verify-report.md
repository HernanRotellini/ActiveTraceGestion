# C-17 Verification Report — Programas y Fechas Académicas

**Date**: 2026-06-07
**Status**: ✅ PASS — 70/70 tests passing

---

## Test Results

| Suite | Tests | Pass | Fail | Error |
|-------|-------|------|------|-------|
| Models | 13 | 13 | 0 | 0 |
| Repositories | 14 | 14 | 0 | 0 |
| Services | 20 | 20 | 0 | 0 |
| API | 23 | 23 | 0 | 0 |
| **Total** | **70** | **70** | **0** | **0** |

## Requirement Coverage

### Programas de Materia (`specs/programas-materia/spec.md`)

| Requirement | Test Coverage | Result |
|-------------|--------------|--------|
| Crear programa con contexto válido | `test_crear_programa_con_contexto_valido`, `test_create_programa_valido`, `test_create_programa_returns_201` | ✅ |
| Rechazar contexto cross-tenant | `test_programa_cross_tenant_aislamiento`, `test_create_programa_rechaza_contexto_cross_tenant`, `test_create_programa_cross_tenant_returns_404` | ✅ |
| Listar/filtrar por contexto académico | `test_list_programas_active`, `test_list_programas_filtros`, `test_list_programas` | ✅ |
| Detalle de programa existente | `test_create_get_programa`, `test_get_programa`, `test_get_programa_returns_200` | ✅ |
| Actualizar metadatos | `test_update_programa` (repo + service), `test_update_programa_returns_200` | ✅ |
| Soft delete (excluir de activos) | `test_programa_soft_delete_excluye`, `test_soft_delete_programa`, `test_delete_programa_soft_delete`, `test_delete_programa_returns_204` | ✅ |
| Proteger endpoints con JWT + permiso | `test_create_programa_missing_permission_returns_403`, `test_permission_guard_returns_403` | ✅ |
| Rechazar tenant desde body/path | `test_create_programa_extra_fields_rejected_returns_422`, `test_create_fecha_extra_fields_rejected` | ✅ |
| Campos obligatorios en modelo | `test_programa_requiere_campos_obligatorios` | ✅ |
| Unicidad por título en mismo contexto | `test_programa_duplicado_titulo_rechazado` | ✅ |
| Mismo título diferente materia OK | `test_programa_mismo_titulo_diferente_materia_ok` | ✅ |
| Referencia de archivo opaca | `test_crear_programa_con_contexto_valido` (valor opaco sin interpretación) | ✅ |

### Fechas Académicas (`specs/fechas-academicas/spec.md`)

| Requirement | Test Coverage | Result |
|-------------|--------------|--------|
| Crear fecha académica válida | `test_crear_fecha_con_contexto_y_tipo`, `test_create_fecha_valida`, `test_create_fecha_returns_201` | ✅ |
| Rechazar duplicado activo | `test_fecha_duplicado_rechazado`, `test_fecha_duplicado_mismo_contexto_rechazado`, `test_create_fecha_rechaza_duplicado`, `test_create_fecha_duplicate_returns_409` | ✅ |
| Mismo contexto diferente tipo OK | `test_fecha_misma_materia_diferente_tipo_ok`, `test_create_fecha_mismo_contexto_diferente_tipo_ok` | ✅ |
| Actualizar fecha | `test_update_fecha` (repo + service), `test_update_fecha_returns_200` | ✅ |
| Soft delete | `test_fecha_soft_delete_excluye`, `test_soft_delete_fecha`, `test_delete_fecha_soft_delete`, `test_delete_fecha_returns_204` | ✅ |
| Listado tabular filtrado | `test_list_fechas_active`, `test_list_fechas_filtros`, `test_list_fechas`, `test_list_fechas_filters` | ✅ |
| Consulta calendario por rango | `test_list_fechas_date_range`, `test_list_calendario`, `test_list_calendario_by_date_range` | ✅ |
| Fragmento LMS (con fechas) | `test_generate_lms_fragment_con_fechas`, `test_generate_lms_fragment_orden_cronologico`, `test_get_lms_fragment_returns_html` | ✅ |
| Fragmento LMS (sin fechas) | `test_generate_lms_fragment_sin_fechas`, `test_get_lms_fragment_empty_returns_message` | ✅ |
| Proteger API con JWT + permiso | `test_create_programa_missing_permission_returns_403`, `test_permission_guard_returns_403` | ✅ |
| Aislamiento cross-tenant | `test_fecha_cross_tenant_aislamiento`, `test_cross_tenant_aislamiento` (repo), `test_create_fecha_cross_tenant_rejected` | ✅ |
| TipoFechaAcademica enum | `test_tipo_fecha_academica_enum_values` | ✅ |

## Design Decisions Verification

| Decision | Check | Result |
|----------|-------|--------|
| Referencia de archivo opaca (no path local) | `referencia_archivo` stored as string, no path validation logic | ✅ |
| Contexto validado por FKs existentes | Services validate `materia_id`, `carrera_id`, `cohorte_id` existence + tenant scope | ✅ |
| Listados separados sobre mismo repo | Repository `list()` with filters; service exposes tabular/calendar views | ✅ |
| Fragmento LMS determinístico | `generate_lms_fragment()` pure function, HTML output, no side effects | ✅ |
| Unicidad funcional por contexto | Unique constraints on `(tenant_id, materia_id, cohorte_id, tipo, numero, periodo)` for fechas and `(tenant_id, materia_id, carrera_id, cohorte_id, titulo)` for programas | ✅ |

## Hard Rules Compliance

| Rule | Check | Result |
|------|-------|--------|
| Pydantic v2 `extra='forbid'` | Schemas have `model_config = ConfigDict(extra='forbid')` | ✅ |
| snake_case Python | Functions, variables, column names in snake_case | ✅ |
| ≤500 LOC backend files | All C-17 files < 200 LOC | ✅ |
| tenant_id in every table | Both models have `tenant_id` FK | ✅ |
| Soft delete | Both models use `SoftDeleteMixin` | ✅ |
| Clean Architecture | Queries only in repos, logic in services, no DB in routers | ✅ |
| Tests against real DB | All tests use `db_engine` → real PostgreSQL | ✅ |
| Stdout noise | No `print()` or logging in application code | ✅ |

## Infrastructure Note

Tests were executed inside the `active-trace-api-1` Docker container (Linux) because `asyncpg` on Windows (Python 3.11 from Microsoft Store) cannot connect to Docker-hosted PostgreSQL — a known `ConnectionDoesNotExistError` with Docker Desktop on Windows. The conftest already applies `WindowsSelectorEventLoopPolicy()` and `ssl=False` but the host-side asyncpg build still fails.

---

**Result**: ✅ VERIFIED — All 70 tests pass, all spec requirements covered, all design decisions respected.
