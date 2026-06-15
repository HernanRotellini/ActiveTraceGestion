## Context

El change `fix-admin-api-contract` agregó la columna `descripcion` en Carrera y los campos `carga_horaria`, `carrera_id`, `cohorte_id` en Materia, pero los schemas de update (PATCH) y los formularios frontend no se actualizaron para enviar/persistir todos los campos mostrados. Como resultado:

- `descripcion` de Carreras se muestra en frontend pero nunca se envía al crear o actualizar
- `codigo` y `carga_horaria` de Materias se muestran en frontend pero no se envían en PATCH
- `carrera_id` de Cohortes se envía en PATCH pero el backend lo rechazaría con 422 (por `extra="forbid"`)
- `activo` se muestra como badge en todas las entidades pero no tiene control de edición

### Estado actual por capa

```
FRONTEND                    BACKEND                     BD
─────────                   ───────                     ──
Carreras:
  nombre  ✅ → PATCH ✅     ✅ acepta                   ✅ columna
  codigo  ✅ → PATCH ✅     ✅ acepta                   ✅ columna
  descrip ⚠️ → NO envía     ❌ No acepta                ✅ columna (existe)
  activo  solo badge         estado aceptado pero no UI  ✅ columna estado

Cohortes:
  nombre  ✅ → PATCH ⚠️     ✅ acepta                   ✅ columna
  anio    ✅ → PATCH ⚠️     ✅ acepta                   ✅ columna
  activo  solo badge         ❌ No hay control           ✅ columna estado

Materias:
  nombre  ✅ → PATCH ✅     ✅ acepta                   ✅ columna
  codigo  ✅ → PATCH ❌     ❌ No acepta                ✅ columna
  carga_h ⚠️ → NO envía     ❌ No acepta                ✅ columna
  activo  solo badge         estado aceptado pero no UI  ✅ columna estado
```

## Goals / Non-Goals

**Goals:**
- Todos los campos mostrados en formularios de edición se persisten correctamente
- Backend acepta `descripcion` en Carreras (create + update)
- Backend acepta `codigo` y `carga_horaria` en Materias (update)
- Frontend envía todos los campos del formulario en el PATCH
- Frontend NO envía `carrera_id` en PATCH de cohortes (solo en POST)
- Tests actualizados para cubrir los nuevos campos

**Non-Goals:**
- NO agregar toggle UI para `activo`/`estado` (se deja para otro change)
- NO modificar el modelo de datos ni la BD (las columnas ya existen)
- NO agregar `carrera_id`/`cohorte_id` editables en Materia (requeriría lógica de re-asignación más compleja)
- NO refactorizar ni cambiar patrones existentes (TDD, snake_case, etc.)

## Decisions

### Decisión 1: Descripción en CarreraCreate como opcional
- **Opción A**: Hacer `descripcion` requerida en creación → rompe API actual
- **Opción B**: Hacerla opcional (`str | None = None`) y persistir si se envía
- **Decisión**: **Opción B**. La columna ya tiene default `""`, y el frontend la trata como opcional. No rompe compatibilidad.

### Decisión 2: `codigo` en MateriaUpdate como opcional
- **Razonamiento**: El `codigo` es único por tenant. Si se permite cambiar, el service debe validar unicidad como en create. Se agrega validación de duplicado en `update_materia()`.
- **Validación**: Si se envía `codigo` distinto al actual, verificar que no exista ya en el mismo tenant. Si existe → 409 Conflict.

### Decisión 3: No enviar `carrera_id` en PATCH cohortes
- **Problema**: `handleSave` construye `CohortePayload { carrera_id, nombre, anio, vig_desde }` y lo usa tanto para POST como para PATCH. El schema `CohorteUpdate` rechaza `carrera_id` por `extra="forbid"`.
- **Solución**: En `handleSave`, cuando `editId` está presente, omitir `carrera_id` y `vig_desde` del payload (solo enviar nombre/anio).

### Decisión 4: No modificar `MateriaCreate`
- **Razonamiento**: `MateriaCreate` solo tiene `codigo` y `nombre`, igual que ahora. `carga_horaria` no está en el schema de creación, solo en el de update/response. Se puede agregar en otro change si es necesario.

## Risks / Trade-offs

- [**Riesgo**] Al permitir cambiar `codigo` en Materia via PATCH, se podría crear un duplicado. → **Mitigación**: Validar unicidad en `update_materia()` como se hace en `create_materia()`.
- [**Riesgo**] El frontend actualmente trata `carrera_id` y `cohorte_id` como selects de filtro, no como campos editables. Cambiar la asignación de una materia a otra carrera/cohorte requeriría lógica adicional. → **Mitigación**: No se incluye en este change (non-goal explícito).
