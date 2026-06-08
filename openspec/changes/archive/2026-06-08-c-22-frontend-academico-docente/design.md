## Context

El shell SPA (C-21) provee autenticación JWT con refresh transparente, guards (`AuthGuard`, `PermissionGuard`), layout con sidebar (`MainLayout`), ruteo lazy y cliente HTTP centralizado Axios. Actualmente solo existen las features de auth (login, 2FA, recovery).

C-22 agrega 4 feature modules frontend que consumen APIs backend ya implementadas:
- **C-10**: calificaciones (`/api/admin/materias/{id}/calificaciones`, `.../umbral`, `.../importar`)
- **C-11**: análisis (`/api/v1/analisis/materias/{id}/atrasados`, `.../ranking`, `.../notas-finales`)
- **C-12**: comunicaciones (`/api/v1/comunicaciones/preview`, `.../enviar`, `.../{id}`)
- **C-07**: usuarios (`/api/admin/usuarios`)

Cada feature module sigue la estructura existente: `{components,hooks,services,types,pages}`.

## Goals / Non-Goals

**Goals:**
- Proveer 4 feature modules frontend funcionales para el perfil PROFESOR (y TUTOR para monitores)
- Reutilizar el cliente HTTP centralizado con refresh transparente
- Usar TanStack Query para cache y refetch de datos del servidor
- Usar React Hook Form + Zod para formularios con validación tipada
- Implementar lazy loading de páginas (convención existente)
- Sidebar dinámico que muestre secciones según permisos del usuario

**Non-Goals:**
- No se modifican APIs backend ni modelos de datos
- No se implementan features de COORDINADOR/ADMIN (C-23, C-24)
- No se implementa lógica de negocio del lado frontend (todo delega a backend)
- No se implementa el flujo de aprobación de comunicaciones (F3.3) — solo preview + envío directo

## Decisions

### D1 — Estructura de routing
Se amplía `routes/index.tsx` con nuevas rutas hijas dentro del `AuthGuard` → `MainLayout`:

| Ruta | Feature | Guard | Descripción |
|------|---------|-------|-------------|
| `/docente/comisiones` | comisiones | PermissionGuard `calificaciones:ver` | Importación, umbral, atrasados, ranking, notas |
| `/docente/comisiones/:id` | comisiones | PermissionGuard `calificaciones:ver` | Detalle de comisión |
| `/docente/comunicaciones` | comunicaciones | PermissionGuard `comunicacion:enviar` | Preview, envío, tracking |
| `/docente/monitor` | monitores | PermissionGuard `atrasados:ver` | Seguimiento de alumnos |

**Rationale**: Las rutas hijas bajo `/` permiten heredar el layout y guards de sesión. El prefijo `/docente/` agrupa funcionalmente las features del perfil.

### D2 — Feature modules independientes
Cada feature es un módulo autocontenido en `frontend/src/features/<nombre>/`:

```
features/comisiones/
  components/    → ComisionTable, UmbralForm, ImportPreview, AtrasadosTable, RankingTable, NotasFinalesTable
  hooks/         → useCalificaciones, useImportar, useUmbral, useAtrasados, useRanking, useNotasFinales
  services/      → calificaciones.ts (llamadas HTTP)
  types/         → calificaciones.ts (tipos request/response)
  pages/         → ComisionesListPage, ComisionDetailPage

features/entregas-sin-corregir/
  components/    → EntregasTable, ExportButton
  hooks/         → useEntregasPendientes
  services/      → entregas.ts
  types/         → entregas.ts
  pages/         → EntregasPendientesPage

features/comunicaciones/
  components/    → ComunicacionPreview, EnvioForm, TrackingBadge, TrackingTimeline
  hooks/         → usePreview, useEnviar, useTracking
  services/      → comunicaciones.ts
  types/         → comunicaciones.ts
  pages/         → ComunicacionesPage

features/monitores/
  components/    → MonitorFilters, MonitorTable, AlumnoDetail
  hooks/         → useMonitor
  services/      → monitores.ts
  types/         → monitores.ts
  pages/         → MonitorPage
```

**Rationale**: Coincide con la convención existente (ver `features/auth/`). Cada módulo puede desarrollarse y testearse independientemente.

### D3 — Sidebar dinámico por permisos
Se modifica `MainLayout` para leer los permisos del usuario desde el contexto de sesión y mostrar/ocultar secciones:

```typescript
const menuItems = [
  { label: 'Comisiones', path: '/docente/comisiones', permission: 'calificaciones:ver' },
  { label: 'Entregas pendientes', path: '/docente/entregas', permission: 'atrasados:ver' },
  { label: 'Comunicaciones', path: '/docente/comunicaciones', permission: 'comunicacion:enviar' },
  { label: 'Monitor', path: '/docente/monitor', permission: 'atrasados:ver' },
]
```

**Rationale**: Evita mostrar secciones a las que el usuario no tiene acceso. El `PermissionGuard` en ruta es la capa dura; el menú es la capa blanda.

### D4 — TanStack Query para datos del servidor
Cada hook encapsula una query de TanStack Query con stale times apropiados:

- Datos de calificaciones/atrasados: `staleTime: 30_000` (30s, pueden cambiar durante la sesión)
- Preview de comunicación: `staleTime: 0` (cada preview es único)
- Tracking de comunicación: `refetchInterval: 5_000` (5s, polling para tracking en vivo)
- Usuarios para selector: `staleTime: 60_000` (cambian poco)

**Rationale**: TanStack Query es el estándar del proyecto. Los stale times balancean frescura vs. requests.

### D5 — Permisos en servicios, no lógica de negocio
Los services (`services/*.ts`) solo hacen llamadas HTTP. Los hooks deciden qué endpoints llamar. Los componentes renderizan según el estado de las queries. Los permisos se declaran en los guards de ruta y en el menú, no en los services.

**Rationale**: Separación de concerns clara. Los services son intercambiables (mock → real). Los tests de componentes pueden mockear hooks.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| [UX] Polling cada 5s para tracking puede generar carga en el servidor si muchos docentes monitorean simultáneamente | Implementar refetch con `refetchIntervalInBackground: false` (solo polling cuando la pestaña está activa); considerar WebSocket como mejora futura |
| [Dependencia] Si C-10/C-11/C-12 tienen bugs en sus APIs, el frontend falla | El interceptor de Axios centraliza el manejo de errores HTTP; los hooks envuelven en try/catch con notificación toast |
| [Scope creep] Sidebar dinámico puede escalar en complejidad si crecen los permisos | Mantener la lista plana de menuItems; si crece demasiado, refactorizar a un hook `useMenuItems` que filtre permisos |
| [Performance] Carga inicial con 4 features lazy puede tener muchas solicitudes paralelas | React.lazy + Suspense asegura split de chunks; considerar prefetch de rutas más probables |

## Migration Plan

1. Escribir types y services (contrato HTTP) — pueden testearse independientemente
2. Escribir hooks (TanStack Query) — capa de estado
3. Escribir componentes y páginas — render con datos mockeados
4. Registrar rutas en `routes/index.tsx`
5. Actualizar `MainLayout` con sidebar dinámico
6. Tests: Safety net de rutas existentes, luego tests por feature

Rollback: cada feature module puede removerse eliminando su ruta y entrada de menú.
