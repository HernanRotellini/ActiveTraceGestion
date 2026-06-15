## Why

Tras el fix de permisos RBAC, varias pantallas del frontend fallan con `TypeError: Cannot read properties of undefined (reading 'map')`. El backend ahora responde correctamente pero algunos endpoints devuelven `{ "items": null, "total": 0 }` en lugar de `{ "items": [], "total": 0 }` cuando no hay datos. Como los componentes usan `data?.items.map(...)` en lugar de `data?.items?.map(...)`, el `null` se propaga sin optional chaining y crashea la pantalla.

## What Changes

- Cambiar `data?.items.map(...)` → `data?.items?.map(...)` en todos los componentes que iteran sobre listas paginadas de la API
- Cambiar `variable?.items.map(...)` → `variable?.items?.map(...)` para selects/carreras/cohortes anidados
- No modificar lógica de negocio ni estructura de componentes — solo agregar optional chaining en `.map()`

## Capabilities

### New Capabilities
- `null-safe-list-rendering`: Patrón de renderizado seguro para listas paginadas que tolera `items: null` del backend

### Modified Capabilities
<!-- No spec-level requirement changes — solo fix de implementación -->

## Impact

**13 archivos frontend modificados** (solo una línea cada uno, el `.map()`):
- `features/admin/pages/CohortesPage.tsx` (líneas 75, 133)
- `features/admin/pages/MateriasPage.tsx` (líneas 80, 94, 165)
- `features/admin/pages/CarrerasPage.tsx` (línea 124)
- `features/admin/pages/UsuariosPage.tsx` (línea 336)
- `features/admin/pages/AuditoriaLogPage.tsx` (línea 54)
- `features/encuentros/pages/EncuentrosListPage.tsx` (línea 74)
- `features/tareas-internas/pages/TareasListPage.tsx` (línea 115)
- `features/equipos-docentes/pages/EquiposListPage.tsx` (línea 83)
- `features/liquidaciones/pages/LiquidacionHistorialPage.tsx` (línea 28)
- `features/setup-cuatrimestre/pages/SetupCuatrimestrePage.tsx` (línea 96)
