## Context

The frontend sends mutation payloads (`*Payload` TypeScript types) that don't match backend Pydantic `*Create` schemas. Every backend schema uses `extra='forbid'`, so any unknown field causes a 422 error. There are no automated tests validating this contract, so mismatches go undetected until manual testing.

Seven backend schemas are affected: CarreraCreate, CohorteCreate, MateriaCreate, UsuarioCreate, TareaCreate, SalarioBaseCreate, SalarioPlusCreate.

## Goals / Non-Goals

**Goals:**
- Backend tests exist that send the EXACT payloads the frontend constructs and expect 201
- Frontend `*Payload` types match the corresponding backend `*Create` schemas field-for-field
- The test suite documents the contract between frontend and backend

**Non-Goals:**
- Items 8–11 (FacturaCreate, SlotEncuentroCreate, EvaluacionCreate, AsignacionCreate) — these require structural redesign
- Removing frontend fields that are UI-only (e.g., `prioridad` and `fecha_limite` in TareaPayload) — these can stay but must NOT be sent in the API payload
- Refactoring the frontend HTTP layer — only the type definitions are fixed

## Decisions

### 1. Test approach: explicit JSON payloads, not factories
- **Decision**: Write pytest parametrized tests for each endpoint. Each test constructs a raw JSON dict matching the frontend payload (with the ERROR introduced), asserts that it receives 422, then constructs the CORRECT payload and asserts 201.
- **Rationale**: Using explicit JSON dicts rather than Pydantic factory objects makes the test self-documenting — it's obvious exactly what the frontend sends vs. what the backend expects. No indirection.
- **Alternative considered**: A schema-contract library like `openapi-core` to auto-generate tests from the OpenAPI spec. Rejected because the OpenAPI spec doesn't capture frontend intent — we need to test the actual payloads the frontend constructs.

### 2. Test location: backend tests only
- **Decision**: All contract tests live in `backend/tests/contract/` — a new directory.
- **Rationale**: The test sends HTTP requests to the backend API. The frontend is a consumer of this API. The backend test infrastructure (pytest, test client, DB) already exists.
- **Alternative considered**: Frontend tests using MSW or similar. Rejected because backend `extra='forbid'` behavior is the enforcement mechanism — testing from the backend side is more direct.

### 3. Fix order: types first, tests second
- **Decision**: First fix all `*Payload` types, then create tests proving they work.
- **Rationale**: Tests should validate the CORRECT behavior, not document bugs. Write the tests after fixing the types so tests pass from the start.

### 4. Per-item fix strategy
Each item follows the same pattern:
1. Edit the TypeScript `*Payload` interface: remove fields not in backend schema, rename mismatched fields, add missing required fields
2. Cascade fixes to any code referencing removed/renamed fields
3. Write a backend contract test that verifies the corrected payload receives 201

### 5. Field removal vs. field preservation for UI-only data
- **Decision**: Fields that exist ONLY in the frontend UI (not in the backend model) are removed from `*Payload` but MAY remain in the frontend `*` (response) type or component state. The `*Payload` is strictly the API request body.
- **Example**: `prioridad` and `fecha_limite` in TareaPayload are removed from the payload but stay in the Tarea UI response type. If needed for POST, they'd be added to the backend schema in a future change.

## Fix Mapping

| # | Frontend Payload | Backend Schema | Fix |
|---|-----------------|----------------|-----|
| 1 | CarreraPayload | CarreraCreate | Remove `descripcion`, `activo` |
| 2 | CohortePayload | CohorteCreate | Remove `activo`, add `vig_desde: string` |
| 3 | MateriaPayload | MateriaCreate | Remove `carrera_id`, `cohorte_id`, `carga_horaria`, `activo` |
| 4 | UsuarioAdminPayload | UsuarioCreate | Remove `password`, `roles`, `activo`; add `apellidos`, `cuil`, `telefono`, `direccion`, `legajo`, `banco`, `facturador` |
| 5 | TareaPayload | TareaCreate | Rename `asignado_id` → `asignado_a`; remove `prioridad`, `fecha_limite` |
| 6 | SalarioBasePayload | SalarioBaseCreate | Rename `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta` |
| 7 | PlusPayload | SalarioPlusCreate | Rename `clave` → `grupo`, `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta` |

### 6. URL path correction

The frontend API services use incorrect URL paths that don't match the backend route definitions. This is a critical issue — without fixing URLs, no API calls can succeed regardless of payload correctness.

The backend routes use `prefix` in each router (e.g., `/api/admin` for estructura_academica, `/api/tareas` for tareas), while the frontend hardcodes paths based on tags or feature names (e.g., `/estructura-academica/carreras` instead of `/admin/carreras`).

Correction mapping:

| Frontend (base /api + path) | Backend actual | Fix |
|----------------------------|----------------|-----|
| `/api/estructura-academica/carreras` | `/api/admin/carreras` | Change path to `/admin/carreras` |
| `/api/estructura-academica/cohortes` | `/api/admin/cohortes` | Change path to `/admin/cohortes` |
| `/api/estructura-academica/materias` | `/api/admin/materias` | Change path to `/admin/materias` |
| `/api/usuarios` | `/api/admin/usuarios` | Change path to `/admin/usuarios` |
| `/api/tareas-internas` | `/api/tareas` | Change path to `/tareas` |
| `/api/grilla-salarial/salarios-base` | `/api/liquidaciones/grilla/bases` | Change path to `/liquidaciones/grilla/bases` |
| `/api/grilla-salarial/plus` | `/api/liquidaciones/grilla/pluses` | Change path to `/liquidaciones/grilla/pluses` |
| `/api/facturas-docentes` | `/api/facturas` | Change path to `/facturas` |

Note: `/api/admin/avisos` ✅ already matches. Auth endpoints ✅ already match.

## Risks / Trade-offs

- [R] Removing frontend payload fields may break UI forms that bind to the payload type. → **Mitigation**: The payload type is only used for API mutation calls. UI forms typically bind to a separate form state or a full entity type (e.g., `Carrera` not `CarreraPayload`). Verify each form after the type change.
- [R] UsuarioAdminPayload loses `password`, but the user creation flow doesn't have a separate password field in UsuarioCreate. → **Mitigation**: Check the backend/API route for user creation — password may be set via a separate mechanism or the backend may need a different creation flow. This is a special case to investigate.
- [R] Frontend HTTP service files may construct payloads from multiple sources, so changing the type may not be enough. → **Mitigation**: After changing the type, check each service function to ensure it sends exactly the typed fields.
- [R] URL path changes may affect relative imports or route param parsing. → **Mitigation**: The Axios client prepends the base URL, so only the path portion changes. Route params (like `{id}`) remain unchanged.
