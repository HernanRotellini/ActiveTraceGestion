## ADDED Requirements

### Requirement: Calcular vista previa de liquidación
El sistema SHALL calcular una vista previa de liquidación por cohorte y período, usando asignaciones vigentes, salario base vigente, mapeo Materia→Plus y acumulación de Plus por comisión activa.

#### Scenario: Base y plus acumulado por comisiones
- **WHEN** FINANZAS calcula la liquidación de una cohorte y período donde un PROFESOR tiene tres comisiones activas de materias mapeadas a `PROG`
- **THEN** el sistema calcula `monto_base + 3 × Plus(PROG, PROFESOR)` para ese docente

#### Scenario: Materia sin clave aporta cero Plus
- **WHEN** una asignación vigente corresponde a una materia sin clave Plus vigente
- **THEN** el sistema incluye la base si corresponde y suma cero al componente Plus por esa materia

#### Scenario: Grilla vigente por período
- **WHEN** existen grillas vencidas, vigentes y futuras para un rol o grupo
- **THEN** el sistema usa solo la configuración vigente para el período `AAAA-MM` calculado

### Requirement: Segmentar liquidación contable
El sistema SHALL separar la liquidación en segmentos general, NEXO y facturantes, manteniendo total pagable sin facturantes y visualización informativa de facturantes.

#### Scenario: Facturante excluido del total pagable
- **WHEN** un docente facturante tiene asignaciones vigentes en el período
- **THEN** el sistema lo muestra con `excluido_por_factura=true` y no suma su total al total sin factura

#### Scenario: NEXO visible por separado y sumado
- **WHEN** una liquidación incluye un usuario con rol NEXO no facturante
- **THEN** el sistema lo muestra en segmento NEXO y suma su total al resumen general pagable

### Requirement: Cerrar liquidación de forma inmutable
El sistema SHALL permitir cerrar la liquidación de una cohorte y período, persistiendo un snapshot inmutable de importes, comisiones, rol, flags contables y estado Cerrada.

#### Scenario: Cierre persiste snapshot
- **WHEN** FINANZAS cierra una liquidación calculada para una cohorte y período
- **THEN** el sistema persiste filas de liquidación con `estado=Cerrada`, montos y comisiones calculadas

#### Scenario: Liquidación cerrada no se recalcula por cambios de grilla
- **WHEN** una grilla salarial cambia después del cierre
- **THEN** la liquidación cerrada conserva sus montos originales y no se actualiza retroactivamente

#### Scenario: Segundo cierre del mismo período se rechaza
- **WHEN** FINANZAS intenta cerrar nuevamente una cohorte y período ya cerrados
- **THEN** el sistema rechaza la operación para evitar duplicados o mutaciones

### Requirement: Consultar historial y detalle de liquidaciones
El sistema SHALL permitir consultar liquidaciones cerradas por cohorte, período, usuario y segmento contable, siempre acotado al tenant autenticado.

#### Scenario: Historial por período
- **WHEN** FINANZAS consulta liquidaciones cerradas filtrando por período
- **THEN** el sistema devuelve solo liquidaciones del tenant autenticado que coinciden con el filtro

#### Scenario: Detalle tenant-scoped
- **WHEN** un usuario consulta el detalle de una liquidación de otro tenant
- **THEN** el sistema responde como no encontrada y no expone datos cross-tenant

### Requirement: Proteger API de liquidaciones
El sistema SHALL proteger `/api/liquidaciones/*` con JWT, permisos finos, tenant isolation y auditoría de cierre.

#### Scenario: Usuario sin permiso no calcula ni cierra
- **WHEN** un usuario autenticado sin permiso `liquidaciones:calcular_cerrar` intenta calcular o cerrar liquidaciones
- **THEN** el sistema responde 403 y no ejecuta la operación

#### Scenario: Cierre genera auditoría
- **WHEN** FINANZAS cierra una liquidación
- **THEN** el sistema registra un evento de auditoría `LIQUIDACION_CERRAR` con actor, tenant, cohorte, período y cantidad de registros afectados
