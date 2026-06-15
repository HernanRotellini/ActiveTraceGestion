## Why

Las páginas de admin (Carreras, Cohortes, Materias) no muestran datos en el frontend porque el backend devuelve las respuestas en un formato distinto al que el frontend espera. El frontend espera `{ items: [], total: N }` con campos `activo`, `creada_en`, `descripcion`, etc., pero el backend devuelve arrays planos con campos `estado`, `created_at`, y sin campos como `descripcion`, `carga_horaria`, o relaciones como `carrera_nombre`.

## What Changes

### Backend — Schemas de estructura académica
- Envolver listas en `{ items: T[], total: number }` para carreras, cohortes y materias
- Agregar campo `activo: bool` derivado de `estado` en CarreraResponse, CohorteResponse, MateriaResponse
- Agregar campo `creada_en` (alias de `created_at`) en los tres responses
- Agregar `descripcion` a CarreraResponse (con valor por defecto vacío)
- Agregar `carrera_id`, `cohorte_id` a MateriaResponse
- Agregar `carga_horaria` a MateriaResponse
- Agregar `carrera_nombre`, `cohorte_nombre` a MateriaResponse (join desde la DB)

### Backend — Router de estructura académica
- Agregar `PATCH /api/admin/cohortes/{cohorte_id}` (actualmente no existe, solo DELETE)
- Modificar `GET /api/admin/materias` para aceptar query params `carrera_id` y `cohorte_id`
- Modificar `GET /api/admin/cohortes` para aceptar query param `carrera_id` (ya existe)

### Backend — Service de estructura académica
- Modificar `list_materias()` para aceptar filtros por `carrera_id` y `cohorte_id`
- Modificar `list_cohortes()` para aceptar filtro por `carrera_id` (ya existe)
- Modificar `update_materia()` para aceptar `codigo` como campo actualizable
- Agregar `update_cohorte()` al service

## Capabilities

### New Capabilities
- `admin-estructura-api`: API de estructura académica con contrato frontend-compatible — listas envueltas, campos normalizados, filtros por carrera/cohorte

### Modified Capabilities
- *(ninguna — es la primera spec formal para admin-estructura)*

## Impact

- **Backend**: `backend/app/schemas/estructura_academica.py` — extender schemas response
- **Backend**: `backend/app/api/v1/routers/estructura_academica.py` — wrapper response, filtros, PATCH cohortes
- **Backend**: `backend/app/services/estructura_academica.py` — filtros y update_cohorte
- **Frontend**: ningún cambio necesario (el frontend ya espera el contrato correcto)
- **Tests**: actualizar tests existentes para reflejar nuevo formato response
