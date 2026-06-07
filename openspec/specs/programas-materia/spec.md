## ADDED Requirements

### Requirement: Crear programa de materia
El sistema SHALL permitir crear un programa oficial asociado a una materia, carrera y cohorte del tenant autenticado, almacenando un título descriptivo y una referencia de archivo opaca.

#### Scenario: Alta de programa con contexto válido
- **WHEN** un usuario autenticado con permiso `estructura:gestionar` crea un programa con `materia_id`, `carrera_id`, `cohorte_id`, `titulo` y `referencia_archivo` válidos del mismo tenant
- **THEN** el sistema persiste el programa dentro del tenant autenticado y devuelve la referencia de archivo como valor opaco sin interpretarla como path local

#### Scenario: Rechazo de contexto cross-tenant
- **WHEN** un usuario intenta crear un programa usando materia, carrera o cohorte de otro tenant
- **THEN** el sistema rechaza la operación y no crea un programa visible para el tenant autenticado

### Requirement: Consultar y filtrar programas
El sistema SHALL permitir listar y consultar programas de materia filtrando por materia, carrera y cohorte, siempre acotado al tenant autenticado.

#### Scenario: Listado por contexto académico
- **WHEN** un usuario con permiso `estructura:gestionar` lista programas filtrando por materia, carrera o cohorte
- **THEN** el sistema devuelve solo programas no eliminados del tenant autenticado que coinciden con los filtros solicitados

#### Scenario: Detalle de programa existente
- **WHEN** un usuario consulta el detalle de un programa existente en su tenant
- **THEN** el sistema devuelve título, materia, carrera, cohorte, referencia opaca y fecha de carga del programa

### Requirement: Actualizar y eliminar programas
El sistema SHALL permitir actualizar metadatos de un programa y eliminarlo mediante soft delete sin borrar físicamente el registro ni exponerlo en listados activos.

#### Scenario: Actualización de metadatos
- **WHEN** un usuario con permiso `estructura:gestionar` actualiza el título o la referencia opaca de un programa del mismo tenant
- **THEN** el sistema persiste los nuevos valores manteniendo el mismo contexto académico salvo actualización explícita validada

#### Scenario: Soft delete de programa
- **WHEN** un usuario elimina un programa existente
- **THEN** el sistema marca el programa como eliminado y lo excluye de listados activos sin borrarlo físicamente de la base de datos

### Requirement: Proteger API de programas
El sistema SHALL proteger todos los endpoints `/api/programas` con autenticación JWT, permiso `estructura:gestionar` y aislamiento row-level por tenant.

#### Scenario: Usuario sin permiso no opera programas
- **WHEN** un usuario autenticado sin permiso `estructura:gestionar` intenta crear, listar, actualizar o eliminar programas
- **THEN** el sistema responde 403 y no ejecuta la operación solicitada

#### Scenario: Tenant e identidad desde sesión
- **WHEN** una petición incluye `tenant_id` o identidad en body, query o path intentando alterar el contexto
- **THEN** el sistema ignora o rechaza esos valores y usa exclusivamente el JWT verificado para tenant, identidad y permisos
