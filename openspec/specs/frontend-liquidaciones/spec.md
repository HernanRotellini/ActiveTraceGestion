## ADDED Requirements

### Requirement: Vista de liquidaciones del período
El frontend SHALL mostrar una vista del período actual de liquidación con tres segmentos contables: detalle general (roles sin factura), detalle NEXO (cálculo separado), y docentes que facturan (informativo, excluido del total). SHALL incluir KPIs de cabecera ("Total sin factura", "Total con factura") y filtros por cohorte, mes y opcionalmente por docente.

#### Scenario: Vista segmentada con KPIs
- **WHEN** un usuario con permiso `liquidaciones:ver` accede a `/liquidaciones`
- **THEN** se muestra la tabla de liquidación con tres secciones (General, NEXO, Factura) y KPIs de cabecera con totales

#### Scenario: Filtro por mes y cohorte
- **WHEN** el usuario selecciona un mes y cohorte en los filtros
- **THEN** la tabla se actualiza mostrando solo los registros del período filtrado

### Requirement: Cierre de liquidación
El frontend SHALL permitir a FINANZAS cerrar la liquidación del período activo. Una liquidación cerrada SHALL mostrarse como inmutable (sin acciones de edición). SHALL mostrar confirmación antes de cerrar.

#### Scenario: Cierre exitoso
- **WHEN** el usuario con permiso `liquidaciones:ver` hace clic en "Cerrar liquidación" y confirma
- **THEN** el sistema envía POST a `/liquidaciones/{id}/cerrar` y la vista cambia a estado "Cerrada"

#### Scenario: Liquidación ya cerrada
- **WHEN** la liquidación ya está cerrada
- **THEN** el botón de cierre no se muestra y la vista muestra indicador de "Cerrada"

### Requirement: Historial de liquidaciones
El frontend SHALL listar liquidaciones cerradas de períodos anteriores con acceso de solo lectura a cada detalle.

#### Scenario: Navegación al historial
- **WHEN** el usuario hace clic en "Historial" desde la vista de liquidaciones
- **THEN** se navega a `/liquidaciones/historial` con una tabla paginada de períodos cerrados

#### Scenario: Detalle de liquidación cerrada
- **WHEN** el usuario selecciona una liquidación del historial
- **THEN** se muestra la misma vista segmentada pero en modo solo lectura

### Requirement: Grilla salarial
El frontend SHALL gestionar salarios base (por rol con vigencia) y plus (clave, rol, descripción, vigencia). SHALL permitir ABM, filtros por rol y clave, y mapeo materia ↔ clave de plus por período.

#### Scenario: Listar salarios base
- **WHEN** el usuario con permiso `liquidaciones:configurar-salarios` accede a `/liquidaciones/grilla-salarial`
- **THEN** se muestra una tabla con importes por rol y fechas de vigencia

#### Scenario: Crear nuevo salario base
- **WHEN** el usuario completa el formulario de nuevo salario base y envía
- **THEN** se crea el registro y la tabla se actualiza

#### Scenario: Gestionar plus
- **WHEN** el usuario accede a la sección de plus
- **THEN** se muestra la tabla de plus con clave, rol, descripción y vigencia, con opciones ABM

### Requirement: Gestión de facturas
El frontend SHALL mostrar un ABM de comprobantes de docentes que facturan, con filtros por docente, estado (pendiente/abonada), rango de fechas y búsqueda libre. SHALL permitir cambiar estado entre pendiente y abonado.

#### Scenario: Listar facturas con filtros
- **WHEN** el usuario con permiso `liquidaciones:ver` accede a `/liquidaciones/facturas`
- **THEN** se muestra la tabla de facturas con filtros por docente, estado y fechas

#### Scenario: Cambiar estado de factura
- **WHEN** el usuario hace clic en "Marcar como abonada" en una factura pendiente
- **THEN** se envía PATCH y la tabla refleja el nuevo estado
