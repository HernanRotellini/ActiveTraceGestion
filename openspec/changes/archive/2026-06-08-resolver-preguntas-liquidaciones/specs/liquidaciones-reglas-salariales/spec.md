## ADDED Requirements

### Requirement: Configurar claves de Plus por tenant
El sistema SHALL permitir que cada tenant defina su propio catálogo de claves de Plus salarial, con código, descripción, vigencia y valores por rol, sin depender de claves hardcodeadas globales.

#### Scenario: Alta de clave de Plus tenant-scoped
- **WHEN** FINANZAS configura una clave de Plus `PROG` con descripción y valores por rol para un tenant
- **THEN** el sistema persiste esa clave solo dentro del tenant autenticado y no la expone ni reutiliza para otros tenants

#### Scenario: Materia sin clave no genera Plus
- **WHEN** una materia no tiene clave de Plus vigente asociada para el período liquidado
- **THEN** el sistema no suma Plus por esa materia y conserva la liquidación base del rol correspondiente si aplica

### Requirement: Mapear materias a claves de Plus
El sistema SHALL permitir asociar cada materia del tenant a cero o una clave de Plus vigente para un período, usando `Materia` como fuente única del catálogo académico.

#### Scenario: Mapeo explícito materia a clave
- **WHEN** FINANZAS asocia una materia activa a la clave de Plus `PROG`
- **THEN** las comisiones activas de esa materia usan `PROG` para calcular el Plus del rol correspondiente durante la vigencia del mapeo

#### Scenario: Rechazo de mapeo cross-tenant
- **WHEN** se intenta asociar una materia de otro tenant a una clave de Plus del tenant autenticado
- **THEN** el sistema rechaza la operación y no crea un mapeo visible para el tenant autenticado

### Requirement: Acumular Plus por comisión activa
El sistema SHALL calcular el Plus de un docente multiplicando el valor `Plus(clave, rol)` por la cantidad de comisiones activas de materias asociadas a esa clave en el período liquidado.

#### Scenario: Tres comisiones de la misma clave acumulan tres veces
- **WHEN** un PROFESOR tiene tres comisiones activas de materias mapeadas a la clave `PROG` en el período liquidado
- **THEN** el sistema suma `3 × Plus(PROG, PROFESOR)` al monto_plus de la liquidación

#### Scenario: Comisiones de claves diferentes suman por separado
- **WHEN** un docente tiene dos comisiones de clave `PROG` y una comisión de clave `BD`
- **THEN** el sistema suma `2 × Plus(PROG, rol) + 1 × Plus(BD, rol)` al monto_plus

#### Scenario: Sin tope de acumulación por defecto
- **WHEN** un docente tiene más de una comisión activa de la misma clave
- **THEN** el sistema acumula todas las comisiones activas sin aplicar tope, salvo que un cambio futuro introduzca una regla explícita de tope

### Requirement: Evaluar vigencia salarial por período liquidado
El sistema SHALL seleccionar `SalarioBase`, `SalarioPlus` y mapeos Materia→clave vigentes para el período `AAAA-MM` que se está calculando.

#### Scenario: Grilla vigente para el mes seleccionado
- **WHEN** FINANZAS calcula la liquidación de `2026-06`
- **THEN** el sistema usa los registros con vigencia que incluye junio de 2026 y no los registros vencidos o futuros

#### Scenario: Liquidación cerrada conserva snapshot
- **WHEN** una liquidación ya fue cerrada y luego cambia la grilla salarial
- **THEN** el sistema conserva los montos cerrados sin recalcular retroactivamente la liquidación cerrada

### Requirement: Separar docentes facturantes de liquidación general
El sistema SHALL excluir del total pagable Base+Plus a los docentes configurados con modalidad de pago facturante y SHALL gestionarlos mediante el flujo de Facturas.

#### Scenario: Docente facturante excluido del total general
- **WHEN** un docente facturante tiene asignaciones activas en el período liquidado
- **THEN** el sistema lo muestra en el segmento informativo de facturantes y no suma su Base+Plus al total sin factura

#### Scenario: Docente no facturante entra a liquidación general
- **WHEN** un docente no facturante tiene asignaciones activas y datos bancarios requeridos
- **THEN** el sistema lo incluye en la liquidación general Base+Plus del período

### Requirement: Asociar facturas por docente y período
El sistema SHALL registrar facturas como comprobantes globales por docente y período, con detalle libre y referencia opaca al archivo, sin requerir asociación obligatoria a una comisión específica.

#### Scenario: Factura de docente facturante para un período
- **WHEN** FINANZAS registra una factura para un docente facturante en el período `2026-06`
- **THEN** el sistema conserva la factura asociada al docente y período, con estado Pendiente hasta que sea marcada como Abonada

#### Scenario: Factura no valida monto contra liquidación Base Plus
- **WHEN** FINANZAS carga una factura con un monto o detalle informado manualmente
- **THEN** el sistema no bloquea la carga por diferencia contra una liquidación Base+Plus equivalente, porque el docente facturante no forma parte del total pagable de liquidación general
