## Context

El frontend actual tiene implementados los features del perfil PROFESOR/DOCENTE (C-22): comisiones, entregas sin corregir, comunicaciones, monitor de alumnos. El shell (C-21) provee AuthGuard, PermissionGuard, MainLayout con menú dinámico por permisos, lazy loading, y la estructura feature-based. El backend ya expone las APIs que C-23 consumirá (C-08 equipos-docentes, C-13 encuentros, C-14 coloquios, C-15 avisos, C-16 tareas-internas, C-17 fechas-académicas). Este change agrega 7 nuevos feature modules y sus rutas para los perfiles COORDINADOR y ADMIN.

## Goals / Non-Goals

**Goals:**
- Implementar 7 feature modules frontend con páginas lazy-loaded para COORDINADOR/ADMIN
- Cada feature module sigue el patrón establecido: `features/{name}/{components,hooks,services,types,pages}`
- Cada página protegida con `PermissionGuard` usando permisos `modulo:accion` del backend
- Items de menú en MainLayout filtrados por `hasPermission()`
- Tests unitarios para componentes clave de cada feature

**Non-Goals:**
- No se modifica el backend
- No se modifican modelos, schemas, DB ni migraciones
- No se agregan nuevas dependencias externas al frontend
- No se rediseña el layout existente (MainLayout permanece igual, solo se agregan items de menú)

## Decisions

### 1. Feature modules independientes (no un mega-módulo "coordinacion")
Cada feature es su propio módulo (`equipos-docentes/`, `avisos/`, `tareas-internas/`, `monitores/`, `encuentros/`, `coloquios/`, `setup-cuatrimestre/`). Esto mantiene la convención del proyecto, permite lazy loading individual, y evita un módulo monolítico difícil de mantener.
- **Alternativa considerada**: Un solo módulo `coordinacion/` con subcarpetas — rechazada porque rompe la convención de feature modules independientes y dificulta el code-splitting.

### 2. Permisos existentes del backend para route guards
Cada feature usa el permiso `modulo:accion` que su backend respectivo ya define. Esto evita crear nuevos permisos solo para UI.
- `equipos-docentes` → `equipos:ver`, `equipos:asignar`
- `avisos` → `avisos:ver`, `avisos:crear`
- `tareas-internas` → `tareas:ver`, `tareas:asignar`
- `encuentros` → `encuentros:ver`, `encuentros:admin`
- `coloquios` → `coloquios:ver`, `coloquios:admin`
- `setup-cuatrimestre` → `programas:admin`

### 3. Monitores transversales como extensión del monitor existente
El módulo `monitores/` ya existe (C-22). Se extiende con nuevas páginas para dashboards generales (F2.7, F2.9). No se crea un módulo separado.
- **Alternativa considerada**: Crear `monitores-coordinacion/` separado — rechazada porque duplica lógica de filtros y tablas.

### 4. Shared components existentes
Se reutilizan `Card`, `Button`, `Input`, `Spinner`, `Alert` de `shared/components/`. No se crean nuevos componentes compartidos a menos que surja la necesidad durante implementación.

### 5. API services con TanStack Query
Cada feature tiene su propio archivo `services/api.ts` que tipa los endpoints del backend y exporta hooks de TanStack Query. Sigue el patrón de `features/comisiones/services/`.

## Routes structure

| Ruta | Feature | Permiso | Page Component |
|------|---------|---------|----------------|
| `/coordinacion/equipos` | equipos-docentes | `equipos:ver` | EquiposListPage |
| `/coordinacion/equipos/nuevo` | equipos-docentes | `equipos:asignar` | EquipoFormPage |
| `/coordinacion/equipos/:id` | equipos-docentes | `equipos:ver` | EquipoDetailPage |
| `/coordinacion/avisos` | avisos | `avisos:ver` | AvisosListPage |
| `/coordinacion/avisos/nuevo` | avisos | `avisos:crear` | AvisoFormPage |
| `/coordinacion/avisos/:id` | avisos | `avisos:ver` | AvisoDetailPage |
| `/coordinacion/tareas` | tareas-internas | `tareas:ver` | TareasListPage |
| `/coordinacion/tareas/:id` | tareas-internas | `tareas:ver` | TareaDetailPage |
| `/coordinacion/encuentros` | encuentros | `encuentros:ver` | EncuentrosListPage |
| `/coordinacion/encuentros/:id` | encuentros | `encuentros:admin` | EncuentroDetailPage |
| `/coordinacion/coloquios` | coloquios | `coloquios:ver` | ColoquiosListPage |
| `/coordinacion/coloquios/:id` | coloquios | `coloquios:admin` | ColoquioDetailPage |
| `/coordinacion/setup` | setup-cuatrimestre | `programas:admin` | SetupCuatrimestrePage |
| `/monitores/general` | monitores (ext.) | `atrasados:ver` | MonitorGeneralPage |

## Risks / Trade-offs

- **Volumen de código**: 7 feature modules nuevos → estimado ~2500-3500 LOC totales. Mitigación: cada módulo es independiente, permite implementación iterativa.
- **Dependencia de APIs existentes**: Si alguna API de backend no cubre un caso edge, el frontend no puede avanzar. Mitigación: los specs de backend ya están implementados (C-08, C-13, C-14, C-15, C-16, C-17 completados).
- **Menú dinámico puede crecer**: Con 7 nuevos items + los existentes, el sidebar puede volverse largo. Trade-off aceptado por ahora; una futura mejora podría agrupar items por perfil (secciones colapsables).
