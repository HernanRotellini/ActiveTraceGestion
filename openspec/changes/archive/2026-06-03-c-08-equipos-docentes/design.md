## Context

C-08 construye la capa de gestión de equipos docentes sobre el modelo de Asignacion existente (C-07). Los endpoints CRUD individuales de `/api/asignaciones` ya funcionan. Ahora se necesita:

- Vista "mis equipos" para cada docente (F4.2)
- Asignación masiva de docentes (F4.4, RN-30)
- Clonado de equipos entre períodos (F4.5, RN-12)
- Modificación de vigencia general de un equipo (F4.6)
- Exportación de equipo (F4.7)
- Auditoría `ASIGNACION_MODIFICAR` (con placeholder hasta C-05)

No hay cambios de modelo (no se requieren nuevas tablas ni migraciones). Toda la lógica es de orquestación sobre `AsignacionRepository` y `AsignacionService` existentes.

## Goals / Non-Goals

**Goals:**
- Proveer endpoint `GET /api/equipos/mis-equipos` para que cualquier docente vea sus asignaciones con filtros (estado, materia, rol, carrera, cohorte)
- Proveer `POST /api/equipos/asignacion-masiva` para asignar N docentes en bloque a una combinación materia × carrera × cohorte × rol con vigencia
- Proveer `POST /api/equipos/clonar` para duplicar el equipo de un período origen a uno destino (RN-12)
- Proveer `PATCH /api/equipos/vigencia` para actualizar desde/hasta de todas las asignaciones de un equipo
- Proveer `GET /api/equipos/exportar` para descargar CSV del equipo
- Placeholder de auditoría inline para `ASIGNACION_MODIFICAR` (refactor cuando C-05 esté listo)

**Non-Goals:**
- Modificar el modelo Asignacion (no hay cambios de schema)
- Interfaz de usuario (API-only)
- Paginación (los equipos docentes son pequeños, < 100 registros)
- Autorización fina por comisión (el guard `equipos:asignar` ya existe)
- Cola de trabajos para export (se genera sincrónicamente)

## Decisions

1. **EquipoService como servicio nuevo de orquestación** — Las operaciones bulk (masiva, clonar, vigencia en bloque) no pertenecen a `AsignacionService` (que es CRUD individual). Se crea `EquipoService` que orquesta llamadas a `AsignacionRepository` de forma transaccional. Esto mantiene SRP.

2. **Clonado con copy a nivel servicio** — `EquipoService.clone_equipo()`:
   - Toma origen `(materia_id, carrera_id, cohorte_id)` y destino `(carrera_id, cohorte_id)`
   - SELECT todas las asignaciones vigentes del origen
   - Para cada una, crea una nueva asignación con los IDs del destino + nuevas fechas (desde/hasta del nuevo cohorte o parámetros)
   - Se ejecuta dentro de una transacción para atomicidad

3. **Asignación masiva con batch create** — Un solo POST recibe `{ usuario_ids: [...], materia_id, carrera_id, cohorte_id, rol, desde, hasta }`. El servicio itera creando asignaciones en el mismo `flush`. Cada creación valida que el usuario exista en el tenant (reusa validación existente).

4. **Export a CSV** — Se genera el CSV en memoria con `csv.writer` y se devuelve como `StreamingResponse` con `text/csv`. Suficiente para equipos < 100 filas.

5. **Auditoría inline (placeholder)** — Se agrega un helper `audit_action()` en `EquipoService` que registra en un log estructurado JSON por ahora. Cuando C-05 esté implementado, se reemplaza por el sistema de auditoría oficial con `AuditLog` persistente.

6. **Filtros en mis-equipos** — El endpoint acepta query params opcionales: `estado` (vigente/vencida/todas), `materia_id`, `rol`, `carrera_id`, `cohorte_id`. La lógica de filtrado es simple (WHERE clauses en el repo) — no se necesita ElasticSearch ni nada sofisticado para el volumen esperado.

7. **Modificación de vigencia en bloque** — El endpoint recibe `{ materia_id, carrera_id, cohorte_id, desde, hasta }`. Busca todas las asignaciones del equipo y actualiza sus fechas. Si `desde` o `hasta` es nulo, no se modifica ese campo. La operación es transaccional.

## Risks / Trade-offs

- **[Risk]** La auditoría inline (placeholder) quedará hardcodeada y habrá que refactorizar cuando C-05 esté listo → **Mitigation**: el helper `audit_action()` es un método simple de 3 líneas en `EquipoService` — reemplazarlo por el sistema de auditoría real será trivial.
- **[Risk]** Asignación masiva sin validación de unicidad podría crear duplicados → **Mitigation**: se valida antes de insertar que no exista ya una asignación idéntica `(usuario_id, materia_id, carrera_id, cohorte_id, rol)` con vigencia solapada.
- **[Risk]** Clonado con muchas asignaciones podría ser lento → **Mitigation**: los equipos docentes son pequeños (< 100). Si escala, se puede migrar a una operación bulk SQL.
- **[Risk]** Export CSV con caracteres especiales (tildes, ñ) → **Mitigation**: se fuerza UTF-8 BOM para compatibilidad con Excel.
