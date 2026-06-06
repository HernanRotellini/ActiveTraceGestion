## Why

Los COORDINADORES y ADMIN necesitan un canal de comunicación institucional dentro del sistema para publicar novedades, alertas y recordatorios dirigidos a segmentos específicos de usuarios (por rol, materia o cohorte). Actualmente no existe un tablón de avisos nativo — las comunicaciones se limitan a la mensajería saliente (email) del módulo de comunicaciones (C-12). Un tablón de avisos con alcance controlado, vigencia y confirmación de lectura permite reducir la carga de emails y garantizar que la información crítica llegue a los destinatarios correctos.

## What Changes

- Nuevo modelo `Aviso` con alcance (Global/PorMateria/PorCohorte/PorRol), severidad (Info/Advertencia/Crítico), vigencia programada, orden de prioridad y requerimiento opcional de acknowledgment.
- Nuevo modelo `AcknowledgmentAviso` para registrar confirmaciones de lectura.
- API REST `/api/avisos/*`:
  - CRUD de avisos (COORDINADOR/ADMIN) con permiso `avisos:publicar`.
  - Endpoint público para listar avisos visibles al usuario autenticado según su rol/alcance/cohorte.
  - Endpoint de confirmación de lectura (acknowledgment).
  - Endpoints de métricas: contadores de vistas y confirmaciones derivados de `AcknowledgmentAviso`.
- Filtrado automático: un aviso solo es visible si:
  - El usuario está dentro del alcance definido (rol, materia, cohorte).
  - La fecha/hora actual está dentro de la ventana `inicio_en`–`fin_en`.
  - El aviso está marcado como `activo`.
- Permiso `avisos:publicar` en la matriz RBAC para COORDINADOR y ADMIN.
- Migración Alembic con las tablas `aviso` y `acknowledgment_aviso`.
- Auditoría: las operaciones CRUD sobre avisos generan registros en `AuditLog`.

## Capabilities

### New Capabilities
- `avisos-gestion`: Gestión completa del tablón de avisos institucionales — ABM, alcance por rol/materia/cohorte, severidad, vigencia programada, orden de prioridad, requerimiento de acknowledgment, y visualización filtrada según el perfil del destinatario. Incluye confirmación de lectura (acknowledgment) con contadores derivados.

### Modified Capabilities
_(Ninguna — no existen specs previas de avisos)_

## Impact

- **Nuevos modelos**: `Aviso`, `AcknowledgmentAviso` en `backend/app/models/aviso.py`
- **Nuevo repositorio**: `backend/app/repositories/aviso_repository.py` con scope de tenant y filtros de alcance/vigencia
- **Nuevo service**: `backend/app/services/aviso_service.py` con lógica de visibilidad y acknowledgment
- **Nuevo router**: `backend/app/api/v1/routers/avisos.py` con endpoints CRUD + consulta + ack
- **Nuevos schemas Pydantic**: `backend/app/schemas/aviso.py` con `extra='forbid'`
- **Migración Alembic**: nueva migración con tablas `aviso` y `acknowledgment_aviso`
- **Seed RBAC**: agregar permiso `avisos:publicar` a roles COORDINADOR y ADMIN
- **Tests**: ~200-300 líneas cubriendo filtrado por scope, ventana de vigencia, acknowledgment, orden de prioridad, aislamiento tenant
- **Sin impacto en módulos existentes**: no se modifican modelos, servicios ni endpoints previos
