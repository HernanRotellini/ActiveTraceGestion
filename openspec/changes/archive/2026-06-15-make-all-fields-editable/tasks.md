## 1. Backend — Carrera: agregar `descripcion` en create + update

- [x] 1.1 Agregar `descripcion: str | None = None` en `CarreraCreate` schema
- [x] 1.2 Agregar `descripcion: str | None = None` en `CarreraUpdate` schema
- [x] 1.3 Agregar `descripcion` en `EstructuraAcademicaService.create_carrera()` y pasarlo al repo
- [x] 1.4 Agregar `descripcion` en `EstructuraAcademicaService.update_carrera()` y pasarlo al repo
- [x] 1.5 Agregar `descripcion` en `CarreraRepository.update()` — asignar si no es None
- [x] 1.6 Pasar `descripcion=body.descripcion` en router `POST /carreras`
- [x] 1.7 Pasar `descripcion=body.descripcion` en router `PATCH /carreras/{id}`

## 2. Backend — Materia: agregar `codigo` y `carga_horaria` en update

- [x] 2.1 Agregar `codigo: str | None = None` y `carga_horaria: int | None = None` en `MateriaUpdate` schema
- [x] 2.2 Agregar `codigo` y `carga_horaria` en `EstructuraAcademicaService.update_materia()` y pasarlos al repo
- [x] 2.3 Agregar `codigo` y `carga_horaria` en `MateriaRepository.update()` — asignar si no es None
- [x] 2.4 Validar unicidad de `codigo` en `update_materia()` si se envía un codigo distinto al actual → 409 Conflict
- [x] 2.5 Pasar `codigo=body.codigo, carga_horaria=body.carga_horaria` en router `PATCH /materias/{id}`

## 3. Frontend — Carreras: enviar `descripcion` en payload

- [x] 3.1 Agregar `descripcion?: string` en `CarreraPayload` type
- [x] 3.2 En `CarrerasPage.handleSave`, incluir `descripcion` en el payload de create y update

## 4. Frontend — Materias: enviar `codigo` y `carga_horaria` en update

- [x] 4.1 Agregar `carga_horaria?: number` en `MateriaPayload` type
- [x] 4.2 En `MateriasPage.handleSave` (rama edit), incluir `codigo` y `carga_horaria` en el payload

## 5. Frontend — Cohortes: no enviar `carrera_id` en PATCH

- [x] 5.1 En `CohortesPage.handleSave` (rama edit), omitir `carrera_id` y `vig_desde` del payload — enviar solo `{ nombre, anio }`

## 6. Tests

- [x] 6.1 Agregar test: POST carrera con descripcion → 201 con descripcion persistida
- [x] 6.2 Agregar test: POST carrera sin descripcion → 201 con descripcion vacía
- [x] 6.3 Agregar test: PATCH carrera con descripcion → descripcion actualizada
- [x] 6.4 Agregar test: PATCH materia con codigo y carga_horaria → campos actualizados
- [x] 6.5 Agregar test: PATCH materia con codigo duplicado → 409 Conflict
