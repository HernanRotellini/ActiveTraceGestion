## Why

El shell SPA multi-tenant (C-21) ya proporciona autenticación, layout, guards de ruta y cliente HTTP. C-22 agrega las features de gestión académica del perfil **PROFESOR** (y opcionalmente TUTOR) sobre los endpoints backend ya implementados en C-10, C-11 y C-12. Sin esta capa de presentación, los usuarios docentes no pueden operar el sistema: importar calificaciones, detectar atrasados, comunicarse con alumnos ni hacer seguimiento.

## What Changes

- **Feature `comisiones`** (gestión de comisión del PROFESOR):
  - Página de importación de calificaciones con preview y selección de actividades
  - Vista de configuración de umbral de aprobación
  - Tabla de alumnos atrasados con indicadores visuales
  - Ranking de actividades aprobadas
  - Notas finales agrupadas
  - Reportes rápidos con métricas consolidadas
- **Feature `entregas-sin-corregir`**:
  - Vista de detección de entregas finalizadas sin calificación
  - Export a archivo descargable
- **Feature `comunicaciones`** (envío masivo a atrasados):
  - Preview de comunicación antes del envío
  - Confirmación y envío a cola
  - Tracking de estado en tiempo real (Pendiente → Enviando → OK/Fallido/Cancelado)
- **Feature `monitores`** (seguimiento de alumnos):
  - Monitor de seguimiento filtrable para TUTOR/PROFESOR
- **Ruteo**: nuevas rutas protegidas por `PermissionGuard` dentro del `MainLayout`
- **Menú lateral**: nuevas entradas dinámicas según permisos del perfil PROFESOR/TUTOR

## Capabilities

### New Capabilities
- `comisiones-gestion`: importación de calificaciones, configuración de umbral, vista de atrasados, ranking, notas finales y reportes rápidos
- `entregas-pendientes`: detección y exportación de entregas sin corregir
- `comunicaciones-masivas`: preview, envío y tracking de comunicaciones a alumnos
- `monitor-seguimiento`: monitor de estado de alumnos filtrable

### Modified Capabilities
*(ninguna — C-22 no modifica specs existentes, solo crea frontend)*

## Impact

- **Frontend**: 4 nuevos feature modules en `frontend/src/features/` (`comisiones/`, `entregas-sin-corregir/`, `comunicaciones/`, `monitores/`)
- **Ruteo**: nuevo archivo de rutas protegidas para features docentes (o ampliación de `routes/index.tsx`)
- **Menú**: ampliación del `MainLayout` para incluir secciones dinámicas según permisos
- **Dependencias**: consumo de APIs de C-10 (calificaciones), C-11 (análisis/atrasados), C-12 (comunicaciones), C-07 (usuarios)
- **Servicios**: 4 nuevos módulos de servicio (uno por feature) que usan el cliente HTTP centralizado
