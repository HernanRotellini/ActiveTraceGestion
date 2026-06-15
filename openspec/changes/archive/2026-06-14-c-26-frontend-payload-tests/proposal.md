## Why

The frontend sends API payloads that don't match the backend Pydantic schemas, which all use `extra='forbid'`. Every POST/PUT request with unknown fields is silently rejected as 422, making the app effectively unusable for any mutation. We discovered this via manual testing — there are no automated tests validating frontend-to-backend payload compatibility.

## What Changes

1. **Backend tests** — Create tests for each POST/PUT endpoint that send the EXACT payloads the frontend currently constructs. These tests will fail, proving the mismatch.
2. **Frontend fixes** — Align every `*Payload` TypeScript type with its corresponding backend `*Create` schema. Remove unknown fields, rename mismatched fields, and add missing required fields.

Scope is limited to "easy" field-level mismatches (items 1–7):

- **CarreraPayload**: remove `descripcion`, `activo`
- **CohortePayload**: remove `activo`, add `vig_desde`
- **MateriaPayload**: remove `carrera_id`, `cohorte_id`, `carga_horaria`, `activo`
- **UsuarioAdminPayload**: remove `password`, `roles`, `activo`; add `apellidos`, `cuil`, `telefono`, `direccion`, `legajo`, `banco`, `facturador`
- **TareaPayload**: rename `asignado_id` → `asignado_a`; remove `prioridad`, `fecha_limite`
- **SalarioBasePayload**: rename `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta`
- **PlusPayload**: rename `clave` → `grupo`, `importe` → `monto`, `vigencia_desde` → `desde`, `vigencia_hasta` → `hasta`

Items 8–11 (Facturas, Encuentros, Coloquios, Equipos Docentes) involve structural redesign and are excluded from this change.

## Capabilities

### New Capabilities
- `endpoint-payloads`: Validation that every frontend mutation payload matches its backend Pydantic schema, enforced by automated tests

### Modified Capabilities
*(None — no existing spec changes its requirements)*

## Impact

- `frontend/src/features/admin/types/index.ts` — CarreraPayload, CohortePayload, MateriaPayload, UsuarioAdminPayload
- `frontend/src/features/tareas-internas/types/index.ts` — TareaPayload
- `frontend/src/features/liquidaciones/types/index.ts` — SalarioBasePayload, PlusPayload
- `backend/app/schemas/estructura_academica.py` — CarreraCreate, CohorteCreate, MateriaCreate (no changes needed, already correct)
- `backend/app/schemas/usuarios.py` — UsuarioCreate (no changes needed, already correct)
- `backend/app/schemas/tarea.py` — TareaCreate (no changes needed, already correct)
- `backend/app/schemas/liquidaciones.py` — SalarioBaseCreate, SalarioPlusCreate (no changes needed, already correct)
- New test files in `backend/tests/` — one per endpoint payload
