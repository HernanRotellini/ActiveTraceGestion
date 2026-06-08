## ADDED Requirements

### Requirement: CRUD de usuarios del tenant
El frontend SHALL permitir ADMIN gestionar usuarios del tenant con datos personales (nombre, email, DNI, CBU), asignación de roles, filtros por nombre/email/rol, y tabla paginada.

#### Scenario: Listar usuarios
- **WHEN** el usuario con permiso `usuarios:gestionar` accede a `/admin/usuarios`
- **THEN** se muestra una tabla paginada con todos los usuarios del tenant (nombre, email, rol, estado)

#### Scenario: Crear usuario con rol
- **WHEN** el usuario completa el formulario de nuevo usuario con datos personales y selecciona un rol
- **THEN** se crea el usuario y la tabla se actualiza

#### Scenario: Editar usuario
- **WHEN** el usuario selecciona "Editar" en un usuario existente
- **THEN** se navega a un formulario precargado y al enviar se actualiza el registro

#### Scenario: Filtrar usuarios por rol
- **WHEN** el usuario selecciona un rol en el filtro
- **THEN** la tabla muestra solo usuarios con ese rol

### Requirement: Visualización de PII
El frontend SHALL mostrar datos PII (DNI, CBU) solo cuando el backend los devuelva descifrados. SHALL indicar visualmente cuando un campo está cifrado u oculto.

#### Scenario: PII visible con permiso
- **WHEN** el usuario tiene permiso para ver datos sensibles
- **THEN** los campos DNI y CBU se muestran en texto plano

#### Scenario: PII oculta
- **WHEN** el usuario no tiene permiso para ver datos sensibles
- **THEN** los campos muestran "••••" en lugar del valor real
