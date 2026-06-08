## ADDED Requirements

### Requirement: Listado de tareas internas
El sistema SHALL proveer una página con tabla paginada de tareas internas, con columnas título, asignado a, estado, prioridad, fecha límite.

#### Scenario: Listado muestra tareas del tenant
- **WHEN** un usuario con `tareas:ver` navega a `/coordinacion/tareas`
- **THEN** se renderiza una tabla paginada con las tareas internas del tenant

#### Scenario: Filtros combinados
- **WHEN** el usuario aplica filtros por estado, asignado, prioridad o rango de fechas
- **THEN** la tabla se actualiza mostrando solo las tareas que coinciden con todos los filtros

### Requirement: Crear tarea interna
El sistema SHALL permitir crear tareas internas con título, descripción, asignado, prioridad (alta/media/baja), fecha límite y etiquetas.

#### Scenario: Crear tarea exitosamente
- **WHEN** un usuario con `tareas:asignar` completa el formulario de nueva tarea y envía
- **THEN** la tarea se crea en estado "pendiente" y se redirige al detalle

#### Scenario: Campos requeridos validados
- **WHEN** el usuario intenta guardar sin completar título o asignado
- **THEN** el formulario muestra errores de validación en los campos obligatorios

### Requirement: Workflow de estados
El sistema SHALL permitir cambiar el estado de una tarea a través del workflow: pendiente → en_progreso → completada → cerrada.

#### Scenario: Cambiar estado de tarea
- **WHEN** un usuario cambia el estado de una tarea desde la página de detalle
- **THEN** el estado se actualiza y se registra en el timeline de la tarea

#### Scenario: Transiciones válidas
- **WHEN** un usuario intenta cambiar de "pendiente" a "cerrada" directamente
- **THEN** la transición es rechazada (debe pasar por "completada")

### Requirement: Comentarios en tareas
El sistema SHALL permitir agregar comentarios encadenados a una tarea, con autor y timestamp.

#### Scenario: Agregar comentario
- **WHEN** un usuario escribe un comentario en el detalle de una tarea y lo envía
- **THEN** el comentario se agrega al hilo con autor y timestamp

#### Scenario: Timeline de actividad
- **WHEN** un usuario abre el detalle de una tarea
- **THEN** se muestra un timeline con cambios de estado y comentarios en orden cronológico

### Requirement: Asignar tarea a usuario
El sistema SHALL permitir reasignar una tarea a otro usuario del tenant.

#### Scenario: Reasignar tarea
- **WHEN** un usuario con `tareas:asignar` cambia el asignado de una tarea
- **THEN** la tarea se reasigna y queda registrado quién era el asignado anterior
