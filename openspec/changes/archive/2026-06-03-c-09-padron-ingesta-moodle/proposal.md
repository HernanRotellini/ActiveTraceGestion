## Why

El sistema necesita un mecanismo para registrar y mantener actualizado el padrón de alumnos habilitados por materia y cohorte, con soporte para carga manual (archivos `.xlsx`/`.csv`) e integración automática vía Moodle Web Services. Sin esto, los módulos de calificaciones, atrasados y comunicaciones no tienen la base de alumnos sobre la cual operar. Además, se requiere poder vaciar los datos de una materia manteniendo aislamiento por docente (RN-04).

## What Changes

- Nuevos modelos `VersionPadron` y `EntradaPadron` con versionado: cada carga crea una nueva versión; solo una activa por `(materia_id, cohorte_id)`.
- Endpoint para importar padrón desde archivo `.xlsx`/`.csv` con vista previa antes de confirmar.
- Endpoint para importar padrón vía Moodle Web Services (sync nocturna + on-demand).
- Endpoint para vaciar datos de una materia (scope `usuario_id × materia_id`, RN-04).
- Auditoría de todas las operaciones con código `PADRON_CARGAR`.
- Migración de base de datos para `version_padron` y `entrada_padron`.
- Tests de versionado, import, fallback manual, aislamiento tenant y mock Moodle WS.

**Tensión conocida**: RN-05 describe la importación como "upsert destructivo sin historial", mientras que el modelo E6 y el supuesto base #3 establecen un modelo versionado. Este change adopta el **modelo versionado** (E6): al activar una nueva versión, la anterior se desactiva pero se conserva como histórico. La regla RN-05 se reinterpreta como "la versión activa se reemplaza, el histórico se conserva".

## Capabilities

### New Capabilities
- `padron-ingesta`: modelos VersionPadron/EntradaPadron, importación desde archivo (xlsx/csv) con preview, versionado (activar/desactivar versiones), vaciado de datos de materia con scope RN-04, y auditoría PADRON_CARGAR
- `moodle-integracion`: integración con Moodle Web Services para sincronización de usuarios/actividades, sync nocturna programada + on-demand, fallback automático a importación manual si el Moodle no expone WS, manejo de errores con respuesta 502 y reintento

### Modified Capabilities
_(Ninguna — no hay cambios en requirements de specs existentes)_

## Impact

- **Backend**: nuevos modelos (`VersionPadron`, `EntradaPadron`), repositorio, servicio, schema Pydantic, router. Nuevo cliente `integrations/moodle_ws.py`. Nueva migración Alembic.
- **Base de datos**: tablas `version_padron`, `entrada_padron` con tenant isolation y soft delete.
- **Dependencias**: openpyxl (xlsx), csv (stdlib), httpx para Moodle WS.
- **Auditoría**: nuevo código de acción `PADRON_CARGAR`.
