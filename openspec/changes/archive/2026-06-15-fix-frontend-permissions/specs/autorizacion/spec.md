## ADDED Requirements

### Requirement: Backend define permisos de lectura y escritura separados

El backend SHALL definir 9 permisos nuevos con semántica `:ver` (lectura) y `:gestionar` (escritura) separados de los permisos de acción existentes.

| Permiso | Tipo | Descripción |
|---|---|---|
| `calificaciones:ver` | ver | Ver calificaciones y umbrales |
| `equipos:ver` | ver | Ver equipos docentes |
| `equipos:gestionar` | gestionar | Crear y modificar equipos docentes |
| `avisos:ver` | ver | Ver avisos |
| `avisos:gestionar` | gestionar | Crear, editar y eliminar avisos |
| `tareas:ver` | ver | Ver tareas internas |
| `encuentros:ver` | ver | Ver encuentros |
| `coloquios:ver` | ver | Ver coloquios |
| `liquidaciones:ver` | ver | Ver liquidaciones, historial y facturas |

#### Scenario: Nuevos permisos existen en DB
- **WHEN** se ejecuta la migración de permisos
- **THEN** los 9 permisos existen en la tabla `permisos` con sus códigos correctos

#### Scenario: Permisos no rompen seeds existentes
- **WHEN** se corre `alembic upgrade head`
- **THEN** el seed de roles existente no se duplica ni falla

### Requirement: Endpoints GET usan permisos :ver, endpoints de escritura usan :gestionar

Los routers del backend SHALL usar el permiso `:ver` para endpoints GET de lectura y `:gestionar` (o el específico existente) para endpoints POST/PUT/PATCH/DELETE.

#### Scenario: GET /api/calificaciones usa calificaciones:ver
- **WHEN** un usuario sin `calificaciones:importar` pero con `calificaciones:ver` hace GET /api/calificaciones
- **THEN** obtiene 200 en lugar de 403

#### Scenario: GET /api/liquidaciones usa liquidaciones:ver
- **WHEN** un usuario sin `liquidaciones:calcular_cerrar` pero con `liquidaciones:ver` hace GET /api/liquidaciones
- **THEN** obtiene 200 en lugar de 403

#### Scenario: POST /api/avisos usa avisos:gestionar
- **WHEN** un usuario con `avisos:gestionar` hace POST /api/admin/avisos
- **THEN** obtiene 200

#### Scenario: GET /api/admin/avisos usa avisos:ver
- **WHEN** un usuario sin `avisos:publicar` pero con `avisos:ver` hace GET /api/admin/avisos
- **THEN** obtiene 200 en lugar de 403

### Requirement: ADMIN tiene todos los permisos operativos

El rol ADMIN SHALL tener los permisos `liquidaciones:operar_grilla`, `liquidaciones:calcular_cerrar` y `facturas:gestionar` para poder acceder a las pantallas de liquidaciones y facturas.

#### Scenario: ADMIN accede a GET /api/liquidaciones
- **WHEN** un usuario con rol ADMIN hace GET /api/liquidaciones
- **THEN** obtiene 200

#### Scenario: ADMIN accede a GET /api/facturas
- **WHEN** un usuario con rol ADMIN hace GET /api/facturas
- **THEN** obtiene 200

#### Scenario: ADMIN modifica grilla salarial
- **WHEN** un usuario con rol ADMIN hace GET /api/liquidaciones/grilla/bases
- **THEN** obtiene 200

### Requirement: /api/auth/me devuelve permisos del usuario

El endpoint `/api/auth/me` SHALL devolver la lista de permisos efectivos del usuario autenticado, calculada por `AuthorizationService.effective_permissions()`. Además SHALL devolver `nombre` y `apellidos` del usuario desde la tabla `usuarios`.

#### Scenario: Login recibe permisos
- **WHEN** un usuario se loguea y el frontend llama GET /api/auth/me
- **THEN** la respuesta incluye `permissions: list[str]` con los permisos efectivos

#### Scenario: Login recibe nombre legible
- **WHEN** un usuario se loguea y el frontend llama GET /api/auth/me
- **THEN** la respuesta incluye `nombre: str` y `apellidos: str`

#### Scenario: ADMIN tiene permissions no vacío
- **WHEN** un usuario con rol ADMIN llama GET /api/auth/me
- **THEN** `permissions` contiene al menos 18 permisos

### Requirement: Frontend propaga permisos desde /auth/me

El frontend SHALL propagar los permisos recibidos de `/api/auth/me` al `session.user.permissions` durante el login y 2FA.

#### Scenario: Login propaga permissions
- **WHEN** el hook `useLogin` recibe `me.permissions`
- **THEN** llama `setSession()` incluyendo `permissions: me.permissions`

#### Scenario: 2FA propaga permissions
- **WHEN** el hook `useChallenge2fa` recibe `me.permissions`
- **THEN** llama `setSession()` incluyendo `permissions: me.permissions`

#### Scenario: hasPermission funciona para no-ADMIN
- **WHEN** un usuario con rol PROFESOR y permisos cargados llama `hasPermission('calificaciones:ver')`
- **THEN** retorna `true` si tiene el permiso, `false` si no

### Requirement: Frontend sidebar filtra herramientas por permiso

El sidebar del layout principal SHALL mostrar solo las herramientas para las cuales el usuario tiene permiso, usando `hasPermission()`.

#### Scenario: ADMIN ve todas las herramientas
- **WHEN** un usuario ADMIN abre el sidebar
- **THEN** ve todas las opciones del menú

#### Scenario: FINANZAS solo ve liquidaciones, facturas y auditoría
- **WHEN** un usuario FINANZAS abre el sidebar
- **THEN** solo ve Liquidaciones, Grilla salarial, Facturas, Historial y Auditoría

#### Scenario: PROFESOR solo ve comisiones, entregas, comunicaciones y monitor
- **WHEN** un usuario PROFESOR abre el sidebar
- **THEN** solo ve Mis Comisiones, Entregas sin corregir, Comunicaciones y Monitor

### Requirement: Footer del layout muestra nombre legible del usuario

El layout principal SHALL mostrar en la esquina inferior izquierda el nombre y apellido del usuario logueado (obtenido de `/api/auth/me`), junto con su rol. NO debe mostrar el UUID.

#### Scenario: Footer muestra nombre en lugar de UUID
- **WHEN** un usuario está logueado
- **THEN** el footer inferior izquierdo muestra "Nombre Apellido — ROL" en lugar del UUID

#### Scenario: Footer funciona sin nombre disponible
- **WHEN** el usuario no tiene nombre en la respuesta (null)
- **THEN** el footer muestra el email como fallback
