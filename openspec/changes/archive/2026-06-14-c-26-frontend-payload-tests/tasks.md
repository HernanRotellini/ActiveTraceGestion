## 1. Fix frontend CarreraPayload

- [x] 1.1 Remove `descripcion` and `activo` from `CarreraPayload` interface in `frontend/src/features/admin/types/index.ts`
- [x] 1.2 Update all references in `frontend/src/features/admin/services/api.ts` and `frontend/src/features/admin/hooks/useAdmin.ts` if needed
- [x] 1.3 Update any forms that bind to `CarreraPayload` to exclude removed fields

## 2. Fix frontend CohortePayload

- [x] 2.1 Remove `activo` from `CohortePayload` interface
- [x] 2.2 Add `vig_desde: string` (required) to `CohortePayload` interface
- [x] 2.3 Update `frontend/src/features/admin/services/api.ts` to include `vig_desde` in POST payload
- [x] 2.4 Update `frontend/src/features/admin/hooks/useAdmin.ts` to pass `vig_desde` in mutation payloads
- [x] 2.5 Update the cohort creation form to include `vig_desde` field

## 3. Fix frontend MateriaPayload

- [x] 3.1 Remove `carrera_id`, `cohorte_id`, `carga_horaria`, and `activo` from `MateriaPayload` interface
- [x] 3.2 Verify `frontend/src/features/admin/services/api.ts` only sends `codigo` + `nombre`
- [x] 3.3 Update any forms/components that reference removed fields

## 4. Fix frontend UsuarioAdminPayload

- [x] 4.1 Remove `password`, `roles`, and `activo` from `UsuarioAdminPayload` interface
- [x] 4.2 Add `apellidos: string` (required), `cuil?: string`, `telefono?: string`, `direccion?: string`, `legajo?: string`, `banco?: string`, `facturador?: boolean` to `UsuarioAdminPayload`
- [x] 4.3 Update service calls in `frontend/src/features/admin/services/api.ts` for user creation
- [x] 4.4 Investigate how `password` and `roles` should be set (separate endpoints/flow)
- [x] 4.5 Update the user creation form to include new required fields

## 5. Fix frontend TareaPayload

- [x] 5.1 Rename `asignado_id` → `asignado_a` in `TareaPayload` interface in `frontend/src/features/tareas-internas/types/index.ts`
- [x] 5.2 Remove `prioridad` and `fecha_limite` from `TareaPayload`
- [x] 5.3 Update service calls in `frontend/src/features/tareas-internas/services/api.ts`
- [x] 5.4 Update hooks in `frontend/src/features/tareas-internas/hooks/useTareas.ts`

## 6. Fix frontend SalarioBasePayload

- [x] 6.1 Rename `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta` in `SalarioBasePayload` in `frontend/src/features/liquidaciones/types/index.ts`
- [x] 6.2 Update service calls in `frontend/src/features/liquidaciones/services/api.ts`
- [x] 6.3 Update hooks in `frontend/src/features/liquidaciones/hooks/useLiquidaciones.ts`

## 7. Fix frontend PlusPayload

- [x] 7.1 Rename `clave` → `grupo`, `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta` in `PlusPayload` in `frontend/src/features/liquidaciones/types/index.ts`
- [x] 7.2 Update service calls in `frontend/src/features/liquidaciones/services/api.ts`
- [x] 7.3 Update hooks in `frontend/src/features/liquidaciones/hooks/useLiquidaciones.ts`

## 8. Fix frontend API URL paths

- [x] 8.1 Fix Carreras URL: `/estructura-academica/carreras` → `/admin/carreras` in `frontend/src/features/admin/services/api.ts`
- [x] 8.2 Fix Cohortes URL: `/estructura-academica/cohortes` → `/admin/cohortes`
- [x] 8.3 Fix Materias URL: `/estructura-academica/materias` → `/admin/materias`
- [x] 8.4 Fix Usuarios URL: `/usuarios` → `/admin/usuarios`
- [x] 8.5 Fix Tareas URL: `/tareas-internas` → `/tareas` in `frontend/src/features/tareas-internas/services/api.ts`
- [x] 8.6 Fix SalarioBase URL: `/grilla-salarial/salarios-base` → `/liquidaciones/grilla/bases` in `frontend/src/features/liquidaciones/services/api.ts`
- [x] 8.7 Fix Plus URL: `/grilla-salarial/plus` → `/liquidaciones/grilla/pluses`
- [x] 8.8 Fix Facturas URL: `/facturas-docentes` → `/facturas`

## 9. Create backend contract tests

- [x] 9.1 Create `backend/tests/contract/__init__.py`
- [x] 9.2 Create `backend/tests/contract/test_carrera_payload.py` — test correct Carrera payload (201) and extra fields (422)
- [x] 9.3 Create `backend/tests/contract/test_cohorte_payload.py` — test correct Cohorte payload and extra fields
- [x] 9.4 Create `backend/tests/contract/test_materia_payload.py` — test correct Materia payload and extra fields
- [x] 9.5 Create `backend/tests/contract/test_usuario_payload.py` — test correct Usuario payload and extra fields
- [x] 9.6 Create `backend/tests/contract/test_tarea_payload.py` — test correct Tarea payload and extra fields
- [x] 9.7 Create `backend/tests/contract/test_salario_base_payload.py` — test correct SalarioBase payload and extra fields
- [x] 9.8 Create `backend/tests/contract/test_salario_plus_payload.py` — test correct Plus payload and extra fields

## 10. Run and verify

- [x] 10.1 Run all backend contract tests and confirm they pass ✅ (14/14 passed)
- [x] 10.2 Run existing backend test suite to ensure no regressions — 3 pre-existing failures confirmed (unrelated to C-26: test_analisis, test_tareas_api, test_auth_flow)
- [x] 10.3 Verify frontend TypeScript compiles (`npx tsc --noEmit`) ✅
