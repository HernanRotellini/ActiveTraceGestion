## Context

C-18 implementa el dominio CRÍTICO de liquidaciones y honorarios docentes. El sistema ya cuenta con tenants, auth/JWT, RBAC, usuarios/asignaciones, estructura académica, equipos, auditoría y reglas salariales desbloqueadas por `resolver-preguntas-liquidaciones`. La unidad operativa de liquidación es `cohorte × período (AAAA-MM)`; el cálculo usa asignaciones docentes vigentes, grilla salarial versionada, mapeo Materia→clave Plus y separación contable entre docentes no facturantes y facturantes.

Por governance CRÍTICO, la aplicación posterior de este change debe implementarse con checkpoints y Strict TDD. No se debe escribir código de producción sin tests fallidos previos ni modificar reglas contables fuera de lo especificado.

## Goals / Non-Goals

**Goals:**
- Persistir `SalarioBase`, `SalarioPlus`, `MateriaPlus`, `Liquidacion` y `Factura` con tenant isolation, soft delete y auditoría.
- Administrar grilla salarial con vigencia temporal y prevenir solapamientos activos por tenant/rol/grupo/materia.
- Calcular liquidaciones Base+Plus por cohorte y período usando asignaciones vigentes y acumulación de Plus por comisión activa.
- Generar vista previa, detalle, listado/export y cierre inmutable de liquidaciones.
- Gestionar facturas de docentes facturantes como flujo separado con estados Pendiente/Abonada.
- Proteger endpoints con permisos finos `liquidaciones:*`, identidad desde JWT y fail-closed.

**Non-Goals:**
- No integrar bancos, sistemas contables externos ni pagos automáticos.
- No implementar topes de Plus ni reglas especiales fuera de `liquidaciones-reglas-salariales`.
- No validar automáticamente montos de facturas contra Base+Plus equivalente.
- No modificar el modelo de roles ni resolver semánticas adicionales de NEXO más allá de segmentación contable ya definida.

## Decisions

### 1. Grilla salarial como configuración tenant-scoped con vigencia

`SalarioBase`, `SalarioPlus` y `MateriaPlus` serán entidades tenant-scoped con `desde/hasta`, soft delete y constraints para evitar configuraciones vigentes solapadas dentro del mismo tenant.

**Rationale:** RN-31 exige versionado temporal y cálculo con valores vigentes al período. Evitar solapamientos hace el cálculo determinístico.

**Alternativa considerada:** mantener solo el último valor vigente. Se descarta porque rompe historial y recálculo auditable de períodos pasados.

### 2. `MateriaPlus` explícita para mapear Materia→clave

El mapeo no se infiere desde códigos de materia. Se persiste como entidad dedicada con FK a `Materia`, `grupo`, vigencia y tenant.

**Rationale:** cumple la spec archivada `liquidaciones-reglas-salariales`, evita reglas implícitas y permite auditar cambios de grilla.

### 3. Servicio de cálculo puro sobre repositories

El cálculo de liquidación vivirá en services, pero toda query se hará en repositories. El service recibe `tenant_id`, `cohorte_id` y `periodo`, obtiene asignaciones vigentes, usuarios, grilla y mapeos por repositorios, y construye preview/snapshot.

**Rationale:** respeta Clean Architecture: routers → services → repositories → models. La lógica contable queda testeable sin SQL en services.

### 4. Snapshot persistido al cerrar

La vista previa puede recalcularse con la configuración vigente. Al cerrar, se persisten filas `Liquidacion` con montos base, plus, total, comisiones, flags `es_nexo`/`excluido_por_factura` y estado Cerrada.

**Rationale:** RN-22 exige inmutabilidad; el snapshot impide que cambios posteriores de grilla modifiquen liquidaciones cerradas.

### 5. Facturantes fuera del total pagable Base+Plus

Docentes `facturador=true` se muestran en segmento informativo, pero `excluido_por_factura=true` y no suman al total sin factura. Su cobro operativo se gestiona por `Factura`.

**Rationale:** cumple RN-35/RN-38 y evita mezclar flujos contables.

### 6. Permisos finos y audit obligatorio

Los endpoints usarán constantes de permisos, sin strings libres en routers: `liquidaciones:operar_grilla`, `liquidaciones:calcular_cerrar` y `facturas:gestionar` según corresponda. Cierre y cambios críticos generan auditoría.

**Rationale:** reglas duras del proyecto exigen RBAC fino, fail-closed y trazabilidad.

## Risks / Trade-offs

- [Cálculo contable incorrecto] → Mitigación: Strict TDD con casos de base vigente, plus acumulado, facturantes, NEXO y cierre inmutable.
- [Solapamiento de vigencias] → Mitigación: constraints y validaciones service/repository antes de crear o actualizar grilla.
- [Asignaciones incompletas o docentes sin datos bancarios] → Mitigación: preview debe marcar filas no procesables antes del cierre.
- [Performance en cohortes grandes] → Mitigación: índices por `tenant_id`, `cohorte_id`, `periodo`, vigencia y usuario; queries agregadas en repositories.
- [Governance CRÍTICO] → Mitigación: aplicar con checkpoints, no proceder a escritura de código sin aprobación humana explícita si aparece una decisión no cubierta.

## Migration Plan

1. Crear migración Alembic dedicada para tablas salariales, liquidaciones y facturas.
2. Implementar modelos y repositories tenant-scoped.
3. Implementar services de grilla, cálculo/cierre y facturas bajo Strict TDD.
4. Implementar schemas y routers con guards RBAC.
5. Ejecutar suite backend relevante con PostgreSQL real.
6. Rollback: downgrade elimina tablas C-18; en producción, respaldar liquidaciones/facturas antes de downgrade.

## Open Questions

- La spec actual no introduce topes de Plus. Si FINANZAS solicita topes, debe proponerse un change posterior.
- La exportación puede ser JSON/CSV inicial; formato XLSX avanzado puede quedar para un change futuro si no existe patrón reutilizable.
