## ADDED Requirements

### Requirement: Administrar salario base por rol
El sistema SHALL permitir administrar importes de salario base por rol docente, tenant y vigencia temporal, evitando configuraciones vigentes solapadas para el mismo rol.

#### Scenario: Alta de base salarial vigente
- **WHEN** FINANZAS crea una base para el rol PROFESOR con monto, desde y hasta opcional dentro del tenant autenticado
- **THEN** el sistema persiste la base tenant-scoped y la usa para períodos incluidos en su vigencia

#### Scenario: Rechazo de vigencia solapada
- **WHEN** FINANZAS intenta crear otra base PROFESOR cuya vigencia se solapa con una base activa del mismo tenant
- **THEN** el sistema rechaza la operación y conserva la grilla existente sin cambios

### Requirement: Administrar plus salarial por grupo y rol
El sistema SHALL permitir administrar Plus salarial por clave de grupo, rol, descripción, monto y vigencia temporal, siempre acotado al tenant autenticado.

#### Scenario: Alta de plus por grupo y rol
- **WHEN** FINANZAS crea un Plus `PROG` para PROFESOR con vigencia válida
- **THEN** el sistema persiste el Plus y lo deja disponible para cálculos de períodos incluidos en la vigencia

#### Scenario: Tenant no accede a plus de otro tenant
- **WHEN** un usuario de otro tenant lista o consulta Plus salariales
- **THEN** el sistema devuelve solo registros de su tenant y nunca expone los del tenant original

### Requirement: Administrar mapeo Materia a clave Plus
El sistema SHALL permitir asociar una materia del tenant a cero o una clave de Plus vigente, con vigencia temporal y validación cross-tenant.

#### Scenario: Mapeo materia a clave Plus vigente
- **WHEN** FINANZAS asocia una materia activa a la clave `PROG` para una vigencia determinada
- **THEN** el sistema persiste el mapeo y lo usa para calcular Plus durante esa vigencia

#### Scenario: Materia sin mapeo no genera Plus
- **WHEN** una materia no tiene mapeo Materia→Plus vigente para el período calculado
- **THEN** el sistema no suma Plus por sus comisiones

#### Scenario: Rechazo de materia cross-tenant
- **WHEN** FINANZAS intenta mapear una materia perteneciente a otro tenant
- **THEN** el sistema rechaza la operación sin crear mapeo

### Requirement: Proteger API de grilla salarial
El sistema SHALL proteger los endpoints de grilla salarial con JWT, permisos de liquidaciones y tenant isolation.

#### Scenario: Usuario sin permiso no modifica grilla
- **WHEN** un usuario autenticado sin permiso `liquidaciones:operar_grilla` intenta crear, actualizar o eliminar base, plus o mapeos
- **THEN** el sistema responde 403 y no ejecuta la operación

#### Scenario: Payload no controla tenant
- **WHEN** una petición incluye `tenant_id` en body o query intentando alterar el contexto
- **THEN** el sistema rechaza o ignora ese valor y usa exclusivamente el tenant del JWT verificado
