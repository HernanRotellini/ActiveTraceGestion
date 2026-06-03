## ADDED Requirements

### Requirement: Docente puede ver sus equipos
El sistema SHALL proveer un endpoint para que cualquier usuario autenticado con rol docente vea sus propias asignaciones activas.

#### Scenario: Ver mis equipos (todos)
- **WHEN** un PROFESOR autenticado envía un GET a `/api/equipos/mis-equipos`
- **THEN** el sistema retorna todas las asignaciones no eliminadas del usuario en su tenant, cada una con `estado_vigencia` computado

#### Scenario: Filtrar mis equipos por estado
- **WHEN** un PROFESOR envía un GET a `/api/equipos/mis-equipos?estado=vigente`
- **THEN** el sistema retorna solo las asignaciones cuyo `estado_vigencia` es "vigente"

#### Scenario: Filtrar mis equipos por materia
- **WHEN** un PROFESOR envía un GET a `/api/equipos/mis-equipos?materia_id=<uuid>`
- **THEN** el sistema retorna solo las asignaciones que coinciden con esa materia

### Requirement: Coordinador puede asignar docentes en bloque
El sistema SHALL permitir la asignación masiva de múltiples docentes a una misma combinación de materia × carrera × cohorte × rol con vigencia común.

#### Scenario: Asignación masiva exitosa
- **WHEN** un usuario con `equipos:asignar` envía un POST a `/api/equipos/asignacion-masiva` con `{ "usuario_ids": ["<uuid>", "<uuid>"], "materia_id": "<uuid>", "carrera_id": "<uuid>", "cohorte_id": "<uuid>", "rol": "PROFESOR", "desde": "2026-03-01", "hasta": "2026-12-31" }`
- **THEN** el sistema crea todas las asignaciones (una por usuario) y retorna 201 con la lista de asignaciones creadas

#### Scenario: Asignación masiva con usuario inexistente
- **WHEN** un usuario con `equipos:asignar` envía un POST a `/api/equipos/asignacion-masiva` con un `usuario_id` que no existe en el tenant
- **THEN** el sistema retorna 404 Not Found y no crea ninguna asignación

#### Scenario: Asignación masiva sin permiso retorna 403
- **WHEN** un usuario sin `equipos:asignar` envía un POST a `/api/equipos/asignacion-masiva`
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Coordinador puede clonar equipo entre períodos
El sistema SHALL duplicar todas las asignaciones vigentes de un equipo origen hacia un destino, aplicando las fechas del nuevo período (RN-12).

#### Scenario: Clonar equipo exitosamente
- **WHEN** un usuario con `equipos:asignar` envía un POST a `/api/equipos/clonar` con `{ "origen": { "materia_id": "<uuid>", "carrera_id": "<uuid>", "cohorte_id": "<uuid>" }, "destino": { "carrera_id": "<uuid>", "cohorte_id": "<uuid>", "desde": "2027-03-01", "hasta": "2027-12-31" } }`
- **THEN** el sistema duplica todas las asignaciones vigentes del origen al destino con las nuevas fechas y retorna 201 con las asignaciones creadas

#### Scenario: Clonar equipo sin asignaciones origen
- **WHEN** un usuario con `equipos:asignar` envía un POST a `/api/equipos/clonar` y el equipo origen no tiene asignaciones vigentes
- **THEN** el sistema retorna 200 con una lista vacía

#### Scenario: Clonar sin permiso retorna 403
- **WHEN** un usuario sin `equipos:asignar` envía un POST a `/api/equipos/clonar`
- **THEN** el sistema retorna 403 Forbidden

### Requirement: Coordinador puede modificar vigencia general de un equipo
El sistema SHALL actualizar las fechas de vigencia de todas las asignaciones pertenecientes a un equipo en una sola operación (F4.6).

#### Scenario: Modificar vigencia general exitosamente
- **WHEN** un usuario con `equipos:asignar` envía un PATCH a `/api/equipos/vigencia` con `{ "materia_id": "<uuid>", "carrera_id": "<uuid>", "cohorte_id": "<uuid>", "desde": "2026-04-01", "hasta": "2026-12-31" }`
- **THEN** el sistema actualiza los campos `desde` y `hasta` de todas las asignaciones del equipo y retorna 200 con la cantidad de asignaciones afectadas

#### Scenario: Modificar solo desde (hasta no se modifica)
- **WHEN** un usuario con `equipos:asignar` envía un PATCH a `/api/equipos/vigencia` con `{ "materia_id": "<uuid>", "carrera_id": "<uuid>", "cohorte_id": "<uuid>", "desde": "2026-04-01" }` (sin `hasta`)
- **THEN** el sistema actualiza solo `desde` y deja `hasta` sin cambios

### Requirement: Coordinador puede exportar equipo a CSV
El sistema SHALL generar un archivo CSV descargable con el detalle de todas las asignaciones de un equipo (F4.7).

#### Scenario: Exportar equipo exitosamente
- **WHEN** un usuario con `equipos:asignar` envía un GET a `/api/equipos/exportar?materia_id=<uuid>&carrera_id=<uuid>&cohorte_id=<uuid>`
- **THEN** el sistema retorna un archivo CSV con cabeceras `docente,rol,materia,carrera,cohorte,comisiones,desde,hasta,estado_vigencia` y una fila por asignación

#### Scenario: Exportar equipo sin filtros suficientes
- **WHEN** un usuario envía un GET a `/api/equipos/exportar` sin los parámetros requeridos (materia_id, carrera_id, cohorte_id)
- **THEN** el sistema retorna 422 Unprocessable Entity
