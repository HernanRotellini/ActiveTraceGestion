## 1. Feature FINANZAS — Liquidaciones

- [x] 1.1 Crear estructura `features/liquidaciones/{components,hooks,services,types,pages}`
- [x] 1.2 Crear tipos TypeScript para liquidación, grilla salarial, factura
- [x] 1.3 Crear servicio API (`services/api.ts`) con endpoints de liquidaciones, grilla y facturas
- [x] 1.4 Crear hooks TanStack Query: `useLiquidacion`, `useCerrarLiquidacion`, `useHistorial`, `useGrillaSalarial`, `useFacturas`
- [x] 1.5 Crear página `LiquidacionPeriodoPage` con vista segmentada (General / NEXO / Factura) y KPIs de cabecera
- [x] 1.6 Crear componente `LiquidacionTable` para tabla de detalle por segmento
- [x] 1.7 Crear componente `LiquidacionKPIs` para indicadores de totales
- [x] 1.8 Crear página `LiquidacionHistorialPage` con tabla paginada de períodos cerrados
- [x] 1.9 Crear página `GrillaSalarialPage` con ABM de salarios base y plus
- [x] 1.10 Crear componente `SalarioBaseForm` y `PlusForm` para creación/edición
- [x] 1.11 Crear página `FacturasPage` con ABM de comprobantes y cambio de estado
- [x] 1.12 Crear componente `FacturaForm` y `FacturaTable` con filtros

## 2. Feature ADMIN — Estructura Académica

- [x] 2.1 Crear estructura `features/admin/{components,hooks,services,types,pages}` con subdirectorios `estructura/`, `usuarios/`, `auditoria/`
- [x] 2.2 Crear tipos TypeScript para carrera, cohorte, materia
- [x] 2.3 Crear servicio API para estructura académica
- [x] 2.4 Crear hooks TanStack Query: `useCarreras`, `useCohortes`, `useMaterias`
- [x] 2.5 Crear página `CarrerasPage` con ABM y tabla paginada
- [x] 2.6 Crear página `CohortesPage` con ABM filtrado por carrera
- [x] 2.7 Crear página `MateriasPage` con ABM filtrado por carrera/cohorte

## 3. Feature ADMIN — Usuarios

- [x] 3.1 Crear tipos TypeScript para usuario del tenant (con PII)
- [x] 3.2 Crear servicio API para usuarios
- [x] 3.3 Crear hooks TanStack Query: `useUsuarios`, `useCrearUsuario`, `useActualizarUsuario`
- [x] 3.4 Crear página `UsuariosPage` con ABM, tabla paginada y filtros por nombre/email/rol
- [x] 3.5 Manejar visualización de PII (mostrar/ocultar según permiso)

## 4. Feature ADMIN — Auditoría

- [x] 4.1 Crear tipos TypeScript para métricas y log de auditoría
- [x] 4.2 Crear servicio API para panel de auditoría y log
- [x] 4.3 Crear hooks TanStack Query: `useMetricas`, `useLogAuditoria`
- [x] 4.4 Crear página `AuditoriaDashboardPage` con gráfico de acciones por día, estado comunicaciones, interacciones
- [x] 4.5 Crear página `AuditoriaLogPage` con tabla paginada y filtros combinados
- [x] 4.6 Crear componente `AuditoriaFiltros` reutilizable entre dashboard y log

## 5. Routing y Menú

- [x] 5.1 Agregar rutas lazy en `routes/index.tsx` para todas las páginas nuevas
- [x] 5.2 Agregar ítems de menú en `layouts/MainLayout.tsx` con permisos requeridos
- [x] 5.3 Verificar que `PermissionGuard` funciona con los permisos nuevos

## 6. Tests

- [x] 6.1 Tests de componentes: LiquidacionTable, GrillaSalarialForm, FacturaTable
- [x] 6.2 Tests de páginas: vista de liquidación segmentada, cierre exitoso
- [x] 6.3 Tests de páginas: ABM grilla salarial, ABM estructura académica
- [x] 6.4 Tests de páginas: panel de auditoría con filtros, log completo
