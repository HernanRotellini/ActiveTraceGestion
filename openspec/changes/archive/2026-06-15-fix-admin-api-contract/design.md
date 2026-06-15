## Context

El frontend de admin (CarrerasPage, CohortesPage, MateriasPage) espera un contrato API específico:
- Listas envueltas en `{ items: T[], total: number }`
- Campos booleanos `activo` en lugar de strings `estado`
- Campo `creada_en` en lugar de `created_at`
- Campos de relación como `carrera_nombre`, `cohorte_nombre`
- Filtros por `carrera_id` y `cohorte_id` en materias

El backend actual devuelve arrays planos con campos raw de base de datos y sin los joins necesarios. También falta el endpoint `PATCH /api/admin/cohortes/{id}`.

## Goals / Non-Goals

**Goals:**
- Hacer que CarrerasPage, CohortesPage y MateriasPage funcionen sin cambios en el frontend
- Envolver listas en `{ items, total }` para carreras, cohortes, materias
- Agregar campos `activo`, `creada_en`, `descripcion`, etc. a los responses
- Agregar `PATCH /api/admin/cohortes/{cohorte_id}`
- Agregar filtros `carrera_id`/`cohorte_id` a `GET /api/admin/materias`

**Non-Goals:**
- NO cambiar el frontend (el contrato se arregla del lado del backend)
- NO tocar otras features (equipos, encuentros, comunicaciones, etc.)
- NO agregar paginación real (solo wrapper; el total refleja el array completo)
- NO cambiar la DB o el modelo de datos interno

## Decisions

### Decisión 1: Response wrapper en el router (no schema level)
En lugar de cambiar cada schema Pydantic, creamos una función helper `wrap_list(items)` que envuelve la lista en `{"items": items, "total": len(items)}`. Se aplica en los endpoints del router, no en los schemas.

**Opción descartada**: Cambiar `response_model=list[CarreraResponse]` a un schema con items/total. Esto rompería la estructura de tipos y requeriría cambios más profundos.

**Razonamiento**: El wrapper en el router es el punto de menor fricción — los schemas Pydantic se quedan como están, y solo añadimos una capa delgada en la respuesta HTTP.

### Decisión 2: `activo` como campo computado via `@property` o `@computed_field`
Agregamos `activo: bool` y `creada_en: datetime` como `@computed_field` en los schemas Pydantic v2, derivados de `estado` y `created_at` respectivamente.

**Opción descartada**: Modificar el frontend para usar `estado` en lugar de `activo`. El frontend ya está construido y funciona con `activo`.

### Decisión 3: Filtros en materias via query params opcionales
`carrera_id` y `cohorte_id` se agregan como `Query(default=None)` en `GET /api/admin/materias`. El service realiza los joins necesarios y filtra en SQL.

### Decisión 4: Service `update_cohorte()` nuevo
Se agrega el método en `EstructuraAcademicaService` para dar soporte al `PATCH /api/admin/cohortes/{id}`. Acepta `nombre`, `anio`, `vig_desde`, `vig_hasta`.

## Risks / Trade-offs

- **[Riesgo Bajo] Los tests existentes pueden fallar** si verifican el formato plano de respuesta. Se actualizarán para usar `data.items`.
- **[Riesgo Medio] El wrapper `wrap_list` podría omitirse en endpoints nuevos** si no se recuerda usarlo. Mitigación: documentar en el código.
- **[Trade-off] `total` siempre = `len(items)`** porque no hay paginación real. Si en el futuro se agrega paginación, el campo `total` ya está presente y será el total de registros (no el de la página).
- **[No-issue] Backwards compatibility**: No hay clientes externos consumiendo esta API, solo el frontend. Romper el formato no afecta a nadie más.
