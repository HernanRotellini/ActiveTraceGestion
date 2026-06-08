## 1. Tipos y servicios HTTP

- [x] 1.1 Crear `features/comisiones/types/calificaciones.ts` con tipos: `Calificacion`, `ActividadDetectada`, `UmbralConfig`, `AtrasadosResponse`, `RankingItem`, `NotasFinalesItem`
- [x] 1.2 Crear `features/comisiones/services/calificaciones.ts` con funciones: `importarCalificaciones`, `listarCalificaciones`, `configurarUmbral`, `obtenerAtrasados`, `obtenerRanking`, `obtenerNotasFinales`
- [x] 1.3 Crear `features/entregas-sin-corregir/types/entregas.ts` con tipos: `EntregaPendiente`
- [x] 1.4 Crear `features/entregas-sin-corregir/services/entregas.ts` con funciones: `detectarEntregas`, `exportarEntregas`
- [x] 1.5 Crear `features/comunicaciones/types/comunicaciones.ts` con tipos: `PreviewRequest`, `PreviewResponse`, `EnvioRequest`, `EnvioResponse`, `TrackingComunicacion`, `EstadoComunicacion`
- [x] 1.6 Crear `features/comunicaciones/services/comunicaciones.ts` con funciones: `generarPreview`, `enviarComunicacion`, `obtenerTracking`
- [x] 1.7 Crear `features/monitores/types/monitores.ts` con tipos: `MonitorFilters`, `MonitorAlumno`
- [x] 1.8 Crear `features/monitores/services/monitores.ts` con funciones: `obtenerMonitor`, `exportarMonitor`

## 2. Hooks TanStack Query

- [x] 2.1 Crear `features/comisiones/hooks/useCalificaciones.ts` — hook para listar calificaciones (staleTime: 30s)
- [x] 2.2 Crear `features/comisiones/hooks/useImportar.ts` — mutation para importar calificaciones
- [x] 2.3 Crear `features/comisiones/hooks/useUmbral.ts` — query + mutation para leer/configurar umbral
- [x] 2.4 Crear `features/comisiones/hooks/useAtrasados.ts` — query para obtener atrasados
- [x] 2.5 Crear `features/comisiones/hooks/useRanking.ts` — query para obtener ranking
- [x] 2.6 Crear `features/comisiones/hooks/useNotasFinales.ts` — query para notas finales
- [x] 2.7 Crear `features/entregas-sin-corregir/hooks/useEntregasPendientes.ts` — query + mutation para detectar y exportar entregas
- [x] 2.8 Crear `features/comunicaciones/hooks/usePreview.ts` — mutation para generar preview
- [x] 2.9 Crear `features/comunicaciones/hooks/useEnviar.ts` — mutation para enviar comunicación
- [x] 2.10 Crear `features/comunicaciones/hooks/useTracking.ts` — query con polling (refetchInterval: 5000) para tracking
- [x] 2.11 Crear `features/monitores/hooks/useMonitor.ts` — query filtrable con staleTime dinámico

## 3. Componentes y páginas — Comisiones

- [x] 3.1 Crear `features/comisiones/pages/ComisionesListPage.tsx` — lista de comisiones del docente
- [x] 3.2 Crear `features/comisiones/pages/ComisionDetailPage.tsx` — detalle con tabs (calificaciones, atrasados, ranking, notas)
- [x] 3.3 Crear `features/comisiones/components/ImportPreview.tsx` — vista previa de actividades detectadas con checkboxes de selección
- [x] 3.4 Crear `features/comisiones/components/UmbralForm.tsx` — formulario de umbral con validación 0-100
- [x] 3.5 Crear `features/comisiones/components/AtrasadosTable.tsx` — tabla de alumnos atrasados
- [x] 3.6 Crear `features/comisiones/components/RankingTable.tsx` — tabla de ranking
- [x] 3.7 Crear `features/comisiones/components/NotasFinalesTable.tsx` — tabla de notas finales agrupadas
- [x] 3.8 Crear `features/comisiones/components/ReportesRapidos.tsx` — dashboard con KPIs consolidados

## 4. Componentes y páginas — Entregas sin corregir

- [x] 4.1 Crear `features/entregas-sin-corregir/pages/EntregasPendientesPage.tsx` — página de detección y export
- [x] 4.2 Crear `features/entregas-sin-corregir/components/EntregasTable.tsx` — tabla de entregas pendientes
- [x] 4.3 Crear `features/entregas-sin-corregir/components/ExportButton.tsx` — botón de export con estado disabled

## 5. Componentes y páginas — Comunicaciones

- [x] 5.1 Crear `features/comunicaciones/pages/ComunicacionesPage.tsx` — página con selector de alumnos, preview, envío y tracking
- [x] 5.2 Crear `features/comunicaciones/components/ComunicacionPreview.tsx` — render de asunto + cuerpo del preview
- [x] 5.3 Crear `features/comunicaciones/components/EnvioForm.tsx` — formulario de selección de alumnos + botón de envío
- [x] 5.4 Crear `features/comunicaciones/components/TrackingBadge.tsx` — badge de estado (color según estado)
- [x] 5.5 Crear `features/comunicaciones/components/TrackingTimeline.tsx` — timeline de estados con polling

## 6. Componentes y páginas — Monitor

- [x] 6.1 Crear `features/monitores/pages/MonitorPage.tsx` — página con filtros + tabla de resultados
- [x] 6.2 Crear `features/monitores/components/MonitorFilters.tsx` — panel de filtros (nombre, email, comisión, regional, actividad, mínimo)
- [x] 6.3 Crear `features/monitores/components/MonitorTable.tsx` — tabla de resultados con status indicator

## 7. Routing y menú

- [x] 7.1 Registrar rutas docentes en `routes/index.tsx` bajo `/` → `MainLayout`: `/docente/comisiones`, `/docente/comisiones/:id`, `/docente/comunicaciones`, `/docente/monitor`, todas lazy y envueltas en `PermissionGuard`
- [x] 7.2 Actualizar `MainLayout.tsx` con sidebar dinámico que filtra items según permisos del usuario desde el session context
- [x] 7.3 Verificar que `PermissionGuard` ya soporta el formato `modulo:accion` y no requiere cambios

## 8. Tests

- [x] 8.1 Safety net: verificar que tests existentes de C-21 siguen pasando (login render, auth flow, guards)
- [x] 8.2 Test: página ComisionesListPage renderiza lista vacía cuando no hay comisiones
- [x] 8.3 Test: import flow (upload → preview → confirm) con mocks de API
- [x] 8.4 Test: AtrasadosTable renderiza datos y muestra empty state
- [x] 8.5 Test: UmbralForm valida rango 0-100 y submit correcto
- [x] 8.6 Test: ComunicacionPreview muestra asunto + cuerpo correctamente
- [x] 8.7 Test: TrackingBadge muestra color correcto según estado
- [x] 8.8 Test: sidebar dinámico oculta items sin permiso
- [x] 8.9 Test: guard de ruta redirige a /403 sin permiso
