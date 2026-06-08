## ADDED Requirements

### Requirement: Registrar factura docente
El sistema SHALL permitir registrar facturas de docentes facturantes por docente y período, con detalle libre, referencia de archivo opaca, tamaño y estado inicial Pendiente.

#### Scenario: Alta de factura válida
- **WHEN** FINANZAS registra una factura para un usuario facturante del tenant con período, detalle y referencia de archivo
- **THEN** el sistema persiste la factura con estado Pendiente dentro del tenant autenticado

#### Scenario: Rechazo de usuario no facturante
- **WHEN** FINANZAS intenta registrar una factura para un usuario no configurado como facturante
- **THEN** el sistema rechaza la operación y no crea factura

#### Scenario: Referencia de archivo opaca
- **WHEN** FINANZAS registra una factura con `referencia_archivo`
- **THEN** el sistema almacena y devuelve la referencia como string opaco sin interpretarla como path local ni validar existencia física

### Requirement: Gestionar estado de factura
El sistema SHALL permitir cambiar una factura de Pendiente a Abonada registrando fecha de pago, sin permitir transiciones inválidas.

#### Scenario: Marcar factura como abonada
- **WHEN** FINANZAS marca una factura Pendiente como Abonada
- **THEN** el sistema actualiza el estado a Abonada y registra `abonada_at`

#### Scenario: Factura abonada no vuelve a pendiente
- **WHEN** una factura ya está Abonada
- **THEN** el sistema rechaza transiciones que intenten volverla a Pendiente

### Requirement: Listar y filtrar facturas
El sistema SHALL permitir listar facturas por docente, estado, período y rango de fechas, siempre acotadas al tenant autenticado.

#### Scenario: Listado por estado y período
- **WHEN** FINANZAS lista facturas con filtros estado=Pendiente y período=`2026-06`
- **THEN** el sistema devuelve solo facturas activas del tenant autenticado que coinciden con los filtros

#### Scenario: Soft delete excluye factura activa
- **WHEN** FINANZAS elimina una factura
- **THEN** el sistema la marca como eliminada y la excluye de listados activos sin hard delete

### Requirement: Proteger API de facturas
El sistema SHALL proteger `/api/facturas/*` con JWT, permiso `facturas:gestionar`, tenant isolation y schemas Pydantic con `extra='forbid'`.

#### Scenario: Usuario sin permiso no opera facturas
- **WHEN** un usuario autenticado sin permiso `facturas:gestionar` intenta crear, listar, actualizar o eliminar facturas
- **THEN** el sistema responde 403 y no ejecuta la operación

#### Scenario: Payload con tenant_id es rechazado
- **WHEN** una petición de factura incluye `tenant_id` o identidad en el body intentando controlar el contexto
- **THEN** el sistema rechaza el payload o ignora esos valores y usa exclusivamente el JWT verificado
