## Context

C-24 es el frontend de FINANZAS y ADMIN. El backend ya existe (C-18 liquidaciones, C-19 auditoría). El shell frontend ya tiene autenticación, layout, menú dinámico y guards. El módulo de liquidaciones consume los endpoints de `liquidaciones-honorarios`, `grilla-salarial` y `facturas-docentes`. El módulo admin consume `estructura-academica`, `usuarios` y `panel-auditoria-metricas` + `audit-trail`.

## Goals / Non-Goals

**Goals:**
- Cubrir todas las pantallas de FINANZAS (F10.1–F10.6) y ADMIN (F9.1–F9.2 + estructura + usuarios).
- Reutilizar componentes compartidos existentes: `Card`, `Spinner`, `Table`, `Button`, `Pagination`, `PermissionGuard`.
- Seguir exactamente la misma convención de features existentes (`features/{name}/{components,hooks,services,types,pages}`).

**Non-Goals:**
- No se modifica el backend. No hay nuevos endpoints ni cambios de schema.
- No se implementan reportes exportables (PDF, xlsx) — solo visualización en pantalla.

## Decisions

| Decisión | Opción elegida | Alternativas | Razón |
|----------|---------------|--------------|-------|
| Organización de vistas FINANZAS | Feature `liquidaciones` con páginas separadas | Single Page con tabs | Sigue el patrón existente (cada vista es una página lazy-loadable). |
| Organización de vistas ADMIN | Feature `admin` con subdirectorios `estructura/`, `usuarios/`, `auditoria/` | Feature separado por subdominio | Son ~30 archivos, un solo feature evita duplicar hooks/services. Las páginas se agrupan por ruta. |
| Estado de filtros | `useState` local en cada página con objeto de filtros | URL search params / Zustand | Consistente con el patrón existente en `AvisosListPage` y `EquiposListPage`. |
| Organización de consultas TanStack Query | Hook por recurso (`useLiquidaciones`, `useGrillaSalarial`, etc.) | Un solo hook con parámetro tipo | Consistente con `useAvisos`, `useEquipos`, etc. |
| Segmentación liquidación | Tres secciones en una misma página con subtotales | Tres tablas separadas en tabs | La épica F10.6 requiere KPIs comparativos entre segmentos; una sola vista permite ver Total general. |

## Risks / Trade-offs

- [Volumen de archivos] ~55 archivos nuevos → riesgo de inconsistencia en naming. Mitigación: seguir exactamente el naming de features existentes (`camelCase` para hooks, `PascalCase` para componentes/páginas).
- [PII en usuarios] La pantalla de usuarios muestra DNI/CBU → debe respetar el cifrado del backend. El frontend nunca recibe PII en texto plano sin autorización explícita del backend. Mitigación: el backend ya controla esto (C-07). El frontend solo renderiza lo que la API devuelve.
- [Permisos] FINANZAS y ADMIN son roles sensibles. Mitigación: cada ruta usa `PermissionGuard` con el permiso exacto (`liquidaciones:ver`, `liquidaciones:configurar-salarios`, `estructura:gestionar`, `usuarios:gestionar`, `auditoria:ver`). Fail-closed.
