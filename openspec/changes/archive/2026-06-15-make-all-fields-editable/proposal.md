## Why

Actualmente, varios campos que se muestran en el frontend (tablas + formularios de edición) no se persisten al editar porque no viajan en el payload del PATCH o no son aceptados por el backend. Esto causa una experiencia engañosa: el usuario ve el campo, lo modifica, y el cambio se pierde silenciosamente.

Este change unifica frontend y backend para que **todos los campos mostrados en edición sean realmente editables** en Carreras, Cohortes y Materias.

## What Changes

### Backend — Schemas & Services
- **`CarreraCreate`**: agregar campo `descripcion` opcional
- **`CarreraUpdate`**: agregar campo `descripcion` opcional
- **`CarreraRepository.update()`**: agregar asignación de `descripcion`
- **`CarreraService.create_carrera()`**: aceptar y persistir `descripcion`
- **`CarreraService.update_carrera()`**: aceptar y persistir `descripcion`
- **`MateriaUpdate`**: agregar campos `codigo`, `carga_horaria` opcionales
- **`MateriaRepository.update()`**: agregar asignación de `codigo`, `carga_horaria`
- **`MateriaService.update_materia()`**: aceptar y persistir `codigo`, `carga_horaria`
- **Router `PATCH /materias/{id}`**: pasar `codigo`, `carga_horaria` al service

### Frontend — Components & Hooks
- **`CarreraPayload` type**: agregar `descripcion` opcional
- **`CarrerasPage.handleSave`**: incluir `descripcion` en el payload de create y update
- **`MateriaPayload` type**: agregar `carga_horaria` opcional
- **`MateriasPage.handleSave`**: incluir `codigo` y `carga_horaria` en el payload de update
- **`CohortesPage.handleSave`**: NO enviar `carrera_id` en PATCH (solo en POST), porque el schema `CohorteUpdate` rechaza campos extra con `extra="forbid"`

### Especificaciones
- **`estructura-academica` spec**: actualizar escenarios PATCH para reflejar todos los campos editables
- **`frontend-admin-estructura` spec**: actualizar escenarios de edición para reflejar todos los campos

## Capabilities

### Modified Capabilities
- `estructura-academica`: Los endpoints PATCH ahora aceptan todos los campos mostrados en frontend (descripcion en carreras, codigo+carga_horaria en materias)
- `frontend-admin-estructura`: Los formularios de edición ahora envían todos los campos que muestra el formulario

## Impact

- **Backend**: `app/schemas/estructura_academica.py`, `app/repositories/estructura_academica.py`, `app/services/estructura_academica.py`, `app/api/v1/routers/estructura_academica.py`
- **Frontend**: `frontend/src/features/admin/types/index.ts`, `frontend/src/features/admin/pages/CarrerasPage.tsx`, `frontend/src/features/admin/pages/CohortesPage.tsx`, `frontend/src/features/admin/pages/MateriasPage.tsx`
- **Tests**: `backend/tests/test_estructura_academica.py` — actualizar escenarios de PATCH para cubrir nuevos campos
