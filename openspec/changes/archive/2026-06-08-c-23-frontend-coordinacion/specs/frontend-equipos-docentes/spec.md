## ADDED Requirements

### Requirement: Listado de equipos docentes
El sistema SHALL proveer una página con tabla paginada de equipos docentes del tenant, con columnas materia, carrera, cohorte, docentes asignados, vigencia, estado.

#### Scenario: Listado muestra equipos del tenant
- **WHEN** un usuario con `equipos:ver` navega a `/coordinacion/equipos`
- **THEN** se renderiza una tabla paginada con los equipos docentes del tenant activo

#### Scenario: Filtros por materia, carrera, estado
- **WHEN** el usuario aplica filtros en la página de listado
- **THEN** la tabla se actualiza mostrando solo los equipos que coinciden

### Requirement: CRUD individual de equipo docente
El sistema SHALL permitir crear, editar y desactivar asignaciones docentes individuales.

#### Scenario: Crear asignación individual exitosa
- **WHEN** un usuario con `equipos:asignar` completa el formulario y envía
- **THEN** se crea la asignación y se redirige al detalle del equipo

#### Scenario: Editar vigencia de asignación
- **WHEN** un usuario con `equipos:asignar` modifica las fechas de vigencia de una asignación
- **THEN** los cambios se persisten y la tabla refleja la nueva vigencia

### Requirement: Asignación masiva de docentes
El sistema SHALL permitir seleccionar múltiples docentes y asignarlos en bloque a una misma materia×carrera×cohorte×rol con vigencia común.

#### Scenario: Asignación masiva exitosa
- **WHEN** un usuario con `equipos:asignar` selecciona varios docentes y confirma la asignación masiva
- **THEN** se crean todas las asignaciones y se muestra resumen con resultados

#### Scenario: Error parcial en asignación masiva
- **WHEN** uno de los docentes seleccionados ya tiene una asignación activa
- **THEN** el sistema informa el conflicto sin crear asignaciones duplicadas

### Requirement: Clonar equipo desde cuatrimestre anterior
El sistema SHALL permitir clonar todas las asignaciones vigentes de un equipo origen hacia un período destino.

#### Scenario: Clonar equipo exitosamente
- **WHEN** un usuario con `equipos:asignar` selecciona origen y destino y confirma
- **THEN** se duplican las asignaciones y se muestra el nuevo equipo creado

#### Scenario: Clonar sin asignaciones origen
- **WHEN** el equipo origen no tiene asignaciones vigentes para clonar
- **THEN** se muestra un mensaje informativo y no se crean registros

### Requirement: Gestión de vigencia general
El sistema SHALL permitir modificar las fechas de vigencia de todas las asignaciones de un equipo en una sola operación.

#### Scenario: Modificar vigencia general
- **WHEN** un usuario con `equipos:asignar` actualiza las fechas de vigencia general
- **THEN** todas las asignaciones del equipo se actualizan con las nuevas fechas

### Requirement: Exportar equipo a CSV
El sistema SHALL proveer un botón de exportación que descargue un CSV con el detalle de asignaciones del equipo.

#### Scenario: Exportar equipo a CSV
- **WHEN** un usuario hace clic en "Exportar CSV" en la página de detalle de equipo
- **THEN** se descarga un archivo CSV con todas las asignaciones del equipo

### Requirement: Modal de selección de usuarios
El sistema SHALL proveer un selector de usuarios (docentes) con búsqueda para los formularios de asignación.

#### Scenario: Selector busca por nombre o email
- **WHEN** el usuario escribe en el campo de búsqueda del selector
- **THEN** se muestran resultados filtrados de usuarios del tenant con rol docente
