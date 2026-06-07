## ADDED Requirements

### Requirement: Crear fecha académica
El sistema SHALL permitir crear fechas académicas para parciales, TP, coloquios y recuperatorios asociadas a materia y cohorte del tenant autenticado.

#### Scenario: Alta de fecha académica válida
- **WHEN** un usuario con permiso `estructura:gestionar` crea una fecha académica con materia, cohorte, tipo, número, período, fecha y título válidos
- **THEN** el sistema persiste la fecha académica dentro del tenant autenticado y la devuelve con su contexto académico

#### Scenario: Rechazo de duplicado activo
- **WHEN** un usuario intenta crear una fecha académica activa con la misma materia, cohorte, tipo, número y período que otra fecha activa del tenant
- **THEN** el sistema rechaza el duplicado y conserva la fecha existente sin cambios

### Requirement: Gestionar fechas académicas
El sistema SHALL permitir consultar, actualizar y eliminar fechas académicas mediante soft delete, manteniendo integridad de contexto y tenant isolation.

#### Scenario: Actualización de fecha académica
- **WHEN** un usuario con permiso `estructura:gestionar` actualiza fecha, título o contexto validado de una fecha académica del mismo tenant
- **THEN** el sistema persiste los cambios y mantiene la fecha visible en listados activos

#### Scenario: Soft delete de fecha académica
- **WHEN** un usuario elimina una fecha académica existente
- **THEN** el sistema marca la fecha como eliminada y la excluye de listados tabulares y calendario sin borrarla físicamente

### Requirement: Listar fechas en vista tabular y calendario
El sistema SHALL permitir listar fechas académicas con filtros por materia, cohorte, tipo, período y rango de fechas para alimentar vistas tabulares y calendario.

#### Scenario: Listado tabular filtrado
- **WHEN** un usuario lista fechas académicas aplicando filtros de materia, cohorte, tipo o período
- **THEN** el sistema devuelve solo fechas activas del tenant autenticado que coinciden con los filtros, ordenadas de forma estable por fecha y número

#### Scenario: Consulta calendario por rango
- **WHEN** un usuario consulta fechas académicas para un rango de fechas
- **THEN** el sistema devuelve eventos del tenant autenticado dentro del rango, con título, fecha, tipo, materia y cohorte suficientes para una vista calendario

### Requirement: Generar fragmento LMS
El sistema SHALL generar un fragmento de contenido estable y listo para copiar al aula virtual del LMS a partir de fechas académicas filtradas.

#### Scenario: Fragmento con fechas ordenadas
- **WHEN** un usuario solicita el fragmento LMS para una materia y cohorte con fechas académicas activas
- **THEN** el sistema genera contenido HTML o textual con las fechas ordenadas cronológicamente e incluye tipo, número, título y fecha legible

#### Scenario: Fragmento sin fechas
- **WHEN** un usuario solicita el fragmento LMS para un contexto sin fechas activas
- **THEN** el sistema devuelve un contenido vacío o mensaje informativo sin producir error

### Requirement: Proteger API de fechas académicas
El sistema SHALL proteger todos los endpoints `/api/fechas-academicas` con autenticación JWT, permiso `estructura:gestionar` y aislamiento row-level por tenant.

#### Scenario: Usuario sin permiso no opera fechas
- **WHEN** un usuario autenticado sin permiso `estructura:gestionar` intenta crear, listar, actualizar o eliminar fechas académicas
- **THEN** el sistema responde 403 y no ejecuta la operación solicitada

#### Scenario: Tenant siempre viene de la sesión
- **WHEN** una petición incluye `tenant_id` o identidad en body, query o path intentando alterar el contexto
- **THEN** el sistema ignora o rechaza esos valores y usa exclusivamente el JWT verificado para tenant, identidad y permisos
