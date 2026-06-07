## ADDED Requirements

### Requirement: Crear tareas internas asignadas
El sistema SHALL permitir crear tareas internas dentro del tenant autenticado, asignadas a un usuario responsable, creadas por el usuario autenticado y opcionalmente vinculadas a una materia y a un contexto de dominio opaco.

#### Scenario: Alta de tarea con asignación válida
- **WHEN** un usuario autenticado con permiso `tareas:gestionar` crea una tarea con descripción, `asignado_a` válido del mismo tenant y materia opcional del mismo tenant
- **THEN** el sistema crea la tarea en estado `Pendiente`, registra `asignado_por` desde la sesión autenticada y la devuelve sin permitir sobrescribir tenant ni identidad desde la petición

#### Scenario: Rechazo de asignación cross-tenant
- **WHEN** un usuario intenta crear una tarea asignada a un usuario o materia de otro tenant
- **THEN** el sistema rechaza la operación y no crea registros visibles en el tenant autenticado

### Requirement: Consultar mis tareas y administración global
El sistema SHALL exponer listados de tareas acotados al tenant autenticado: una vista de tareas asignadas al usuario actual y una vista global filtrable para coordinación/administración.

#### Scenario: Mis tareas usa identidad de sesión
- **WHEN** un usuario consulta sus tareas
- **THEN** el sistema devuelve solo tareas donde `asignado_a` coincide con el usuario autenticado, sin aceptar parámetros externos para suplantar esa identidad

#### Scenario: Listado global filtrable
- **WHEN** un usuario con permiso `tareas:gestionar` consulta el listado global filtrando por docente asignado, asignador, materia, estado o búsqueda libre
- **THEN** el sistema devuelve solo tareas del tenant autenticado que coinciden con los filtros solicitados

### Requirement: Delegar tareas con trazabilidad
El sistema SHALL permitir delegar o reasignar una tarea a otro usuario del mismo tenant, conservando quién realiza la delegación y quién queda como responsable actual.

#### Scenario: Delegación exitosa
- **WHEN** un usuario con permiso `tareas:gestionar` delega una tarea existente a otro usuario válido del mismo tenant
- **THEN** el sistema actualiza `asignado_a`, registra el actor de la delegación como `asignado_por` o campo de última asignación equivalente, y conserva la tarea dentro del mismo tenant

#### Scenario: Delegación a usuario inválido
- **WHEN** un usuario intenta delegar una tarea a un usuario inexistente, inactivo o perteneciente a otro tenant
- **THEN** el sistema rechaza la delegación y mantiene la asignación anterior sin cambios

### Requirement: Gestionar workflow de estado
El sistema SHALL validar server-side las transiciones de estado de las tareas internas usando los estados `Pendiente`, `En progreso`, `Resuelta` y `Cancelada`.

#### Scenario: Transición válida de progreso a resolución
- **WHEN** una tarea en estado `Pendiente` pasa a `En progreso` y luego a `Resuelta`
- **THEN** el sistema persiste ambas transiciones en orden y refleja el estado final `Resuelta`

#### Scenario: Transición inválida desde estado terminal
- **WHEN** un usuario intenta cambiar una tarea `Resuelta` o `Cancelada` a otro estado
- **THEN** el sistema rechaza la transición y conserva el estado terminal previo

### Requirement: Comentarios en hilo de tarea
El sistema SHALL permitir agregar y consultar comentarios cronológicos asociados a una tarea interna dentro del mismo tenant.

#### Scenario: Agregar comentario a tarea existente
- **WHEN** un usuario autenticado agrega un comentario a una tarea visible en su tenant
- **THEN** el sistema registra el comentario con `autor_id` desde la sesión, fecha de creación y texto asociado a la tarea

#### Scenario: Consultar hilo de comentarios
- **WHEN** un usuario consulta el detalle de una tarea
- **THEN** el sistema devuelve los comentarios de esa tarea ordenados cronológicamente y excluye comentarios de tareas de otros tenants

### Requirement: Proteger endpoints de tareas
El sistema SHALL proteger todos los endpoints `/api/tareas/*` con autenticación JWT, permiso `tareas:gestionar` y aislamiento row-level por tenant.

#### Scenario: Usuario sin permiso no accede
- **WHEN** un usuario autenticado sin permiso `tareas:gestionar` intenta operar sobre `/api/tareas/*`
- **THEN** el sistema responde 403 y no ejecuta la operación solicitada

#### Scenario: Tenant siempre viene de la sesión
- **WHEN** una petición incluye `tenant_id`, `asignado_por` o identidad en body, query o path intentando alterar el contexto
- **THEN** el sistema ignora o rechaza esos valores y usa exclusivamente el JWT verificado para identidad, roles y tenant
