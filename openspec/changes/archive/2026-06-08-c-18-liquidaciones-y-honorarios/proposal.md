## Why

El equipo de FINANZAS necesita calcular, revisar, cerrar y auditar liquidaciones de honorarios docentes por cohorte y período, usando grillas salariales versionadas, Plus por materia/comisión y separación contable entre docentes no facturantes y facturantes. Con `resolver-preguntas-liquidaciones` archivado, las reglas críticas de Plus y facturación ya están definidas y C-18 puede proponerse sin ambigüedad de dominio.

## What Changes

- Agrega modelos, repositories, services, schemas, routers y migración para `SalarioBase`, `SalarioPlus`, `MateriaPlus`, `Liquidacion` y `Factura`.
- Expone administración de grilla salarial: base por rol, plus por clave×rol y mapeo explícito Materia→clave Plus, todo tenant-scoped y con vigencia temporal.
- Implementa cálculo de liquidación por `cohorte × período (AAAA-MM)`: base vigente + acumulación `N × Plus(clave, rol)` por comisión activa.
- Implementa vista previa, detalle, export/listado y cierre inmutable de liquidaciones, con snapshot de montos al cerrar.
- Implementa gestión de facturas de docentes facturantes, con estado Pendiente/Abonada y referencia de archivo opaca.
- Separa segmentos contables: general sin factura, NEXO visible por separado pero sumado, y facturantes informativos excluidos del total pagable Base+Plus.
- Protege endpoints con guards `liquidaciones:*`, identidad/tenant desde JWT y auditoría de acciones críticas como `LIQUIDACION_CERRAR`.
- Mantiene Strict TDD y no usa mocks de DB; todos los tests relevantes usan PostgreSQL real/efímero.

## Capabilities

### New Capabilities
- `grilla-salarial`: ABM de salario base, plus salarial y mapeo Materia→clave Plus con vigencia temporal y tenant isolation.
- `liquidaciones-honorarios`: Cálculo, vista previa, consulta, export/listado y cierre inmutable de liquidaciones Base+Plus por cohorte y período.
- `facturas-docentes`: Gestión de comprobantes de docentes facturantes, estados Pendiente/Abonada y separación del flujo de liquidación general.

### Modified Capabilities

No se modifican requisitos de capacidades existentes. C-18 consume `liquidaciones-reglas-salariales` como contrato ya archivado.

## Impact

- Backend: nuevos modelos ORM, repositories tenant-scoped, services de cálculo, schemas Pydantic v2 y routers `/api/liquidaciones/*`, `/api/facturas/*`.
- Base de datos: migración Alembic para `salario_base`, `salario_plus`, `materia_plus`, `liquidacion`, `factura` con tenant isolation, soft delete, FKs, índices y constraints de vigencia/unicidad.
- Seguridad: dominio CRÍTICO; endpoints solo para FINANZAS/ADMIN según permisos finos, con identidad y tenant derivados exclusivamente de JWT.
- Auditoría: cierre de liquidación y cambios de grilla/facturas generan eventos auditables; liquidación cerrada queda inmutable.
- Tests: grilla vigente por período, acumulación de Plus, facturantes excluidos, cierre inmutable, tenant isolation, permisos, invalid payloads y no DB mocks.
