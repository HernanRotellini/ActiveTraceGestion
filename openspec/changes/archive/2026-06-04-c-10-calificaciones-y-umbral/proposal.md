## Why

El PROFESOR necesita importar las calificaciones de su comisión desde el LMS para poder detectar alumnos atrasados, generar reportes y comunicarse. Sin este módulo, los datos de calificaciones existen solo en Moodle y no pueden ser procesados por activia-trace. Es el paso siguiente en el camino crítico (C-09 → C-10 → C-11 → C-12).

## What Changes

- Nuevos modelos `Calificacion` (numérica/textual, `aprobado` derivado, origen Importado/Manual) y `UmbralMateria` (umbral_pct por asignación, valores aprobatorios)
- Importar calificaciones desde archivo del LMS (F1.1): detectar columnas numéricas (RN-01, sufijo `(Real)`) y textuales (RN-02), vista previa con detección de actividades, selección de actividades a incluir
- Importar reporte de finalización de actividades (F1.2): detectar entregas finalizadas sin calificación (RN-07, RN-08)
- Configurar umbral de aprobación por materia (F2.1, RN-03, defecto 60%)
- Endpoints REST bajo `/api/calificaciones/*` con guard `calificaciones:importar` (PROFESOR, COORDINADOR)
- Auditoría con código `CALIFICACIONES_IMPORTAR`
- Tests: derivación de `aprobado`, import + preview, selección de actividades, umbral por asignación, aislamiento multi-tenant

## Capabilities

### New Capabilities
- `calificaciones-umbral`: Importación de calificaciones desde archivo LMS (xlsx/csv) con preview y selección de actividades, importación de reporte de finalización, configuración de umbral de aprobación por materia, y modelo de datos de calificaciones con derivación automática del campo `aprobado`.

### Modified Capabilities
- *(ninguna — es un módulo de dominio nuevo)*

## Impact

- **Backend**: Nuevos modelos `Calificacion`, `UmbralMateria` y migración Alembic. Nuevos schemas Pydantic. Nuevo repositorio `CalificacionRepository` y `UmbralMateriaRepository`. Nuevo servicio `CalificacionService` con lógica de importación y derivación. Nuevos routers bajo `api/v1/routers/calificaciones.py`. Nuevo parser de archivos LMS (detección de columnas numéricas y textuales).
- **Tests**: tests de unidad para derivación de `aprobado`, tests de integración para import+preview+confirm, tests de umbral por asignación.
- **Dependencia**: Requiere C-09 (padron-ingesta-moodle) — los alumnos destino son las `EntradaPadron` de la versión activa del padrón.
