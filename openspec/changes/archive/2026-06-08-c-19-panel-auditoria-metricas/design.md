## Context

El sistema ya cuenta con:
- Modelo `AuditLog` (E-AUD) con campos completos — C-05
- Repositorio `AuditLogRepository` con `list()` y `count()` paginados con filtros por fecha, actor, acción, materia
- Servicio `AuditService` con métodos de logging por tipo de acción
- Endpoint `GET /api/v1/audit/logs` con filtros, paginación y guard `auditoria:ver`
- Permiso `auditoria:ver` definido y seed en base

Lo que falta para el panel de auditoría y métricas (F9.1, F9.2):
1. Endpoints de **agregaciones** sobre AuditLog (acciones/día, comunicaciones/docente, interacciones/docente×materia)
2. Endpoint de **últimas acciones** con límite configurable (default 200)
3. **Scope `(propio)`** para COORDINADOR: filtrar por sus materias asignadas vía tabla `Asignacion`
4. Tests de todas las agregaciones, filtros y scope

No se requieren nuevos modelos, migraciones, ni cambios en permisos.

## Goals / Non-Goals

**Goals:**
- Exponer 4 endpoints de panel de métricas (solo lectura) bajo `/api/v1/auditoria/panel/*`
- Implementar scope `(propio)` para COORDINADOR filtrando por sus asignaciones docentes
- Mantener compatibilidad con el endpoint existente `GET /api/v1/audit/logs`
- Cobertura ≥90% en reglas de negocio del panel

**Non-Goals:**
- No se modifican modelos de datos ni se crean tablas nuevas
- No se agregan nuevos permisos ni roles
- No se implementa caché de agregaciones (volumen esperado bajo para el dominio)
- No se agrega exportación de métricas (PDF/CSV) — eso pertenece a otro change

## Decisions

### 1. Router separado `/api/v1/auditoria` en vez de extender `/api/v1/audit`
- **Decisión**: Crear `backend/app/api/v1/routers/auditoria.py` con prefijo `/api/v1/auditoria`
- **Rationale**: El router existente `audit.py` expone el log crudo. El panel tiene semántica diferente (agregaciones, métricas). Separarlos mantiene responsabilidad única y ≤500 LOC por archivo.
- **Alternativa**: Extender `audit.py` → lo mezcla todo, supera LOC fácilmente.

### 2. Queries de agregación directas con SQLAlchemy ORM
- **Decisión**: Usar `select(func.count(...), func.date_trunc(...))` con agrupación en SQLAlchemy, sin SQL raw ni vistas materializadas.
- **Rationale**: El volumen de AuditLog es moderado (estimación: <1M registros/tenant/año). Las agregaciones temporales se resuelven con GROUP BY simple. No justifica una vista materializada ni un pipeline separado.
- **Riesgo**: Si el volumen crece, `date_trunc` sin índice en `fecha_hora` puede degradar. → Mitigación: el índice compuesto `(tenant_id, fecha_hora)` ya debería existir de C-05.

### 3. Scope `(propio)` vía JOIN con Asignacion
- **Decisión**: Para COORDINADOR, filtrar los registros de auditoría a solo aquellos donde `materia_id` esté en las materias que el coordinador tiene asignadas (con rol COORDINADOR en Asignacion).
- **Rationale**: Reusa la tabla `Asignacion` existente (C-07). No requiere tabla nueva ni lógica de permisos adicional. ADMIN y FINANZAS ven todo sin filtro.
- **Implementación**: En el service, detectar si el usuario tiene rol ADMIN o FINANZAS → scope completo. Si es COORDINADOR → JOIN con Asignacion filtrando por materias asignadas. Si es otro rol con `auditoria:ver` (no debería ocurrir según matriz de permisos) → scope completo como fallback seguro.

### 4. Endpoint unificado de últimas acciones vs separado
- **Decisión**: Endpoint separado `GET /api/v1/auditoria/panel/ultimas-acciones` con parámetro `max_results` (default 200, max 1000).
- **Rationale**: Es semánticamente diferente de las agregaciones. El endpoint existente `GET /api/v1/audit/logs` ya lista con paginación, pero no tiene limite default 200 ni está orientado a "panel".
- **Alternativa**: Reusar `GET /api/v1/audit/logs` con default limit=200 → rompe compatibilidad. Mejor nuevo endpoint.

### 5. Filtro de estado de actividad (activo/inactivo)
- **Decisión**: No implementar filtro de estado "activo/inactivo" en esta iteración.
- **Rationale**: El concepto "docente inactivo" requiere definir umbrales de inactividad que no están especificados en la KB (días sin acción, comparación con período anterior, etc). Se puede agregar en iteración futura sin cambios de schema.

## Risks / Trade-offs

- **[Rendimiento]** Las agregaciones con `GROUP BY` sobre `fecha_hora` sin índice pueden ser lentas para períodos grandes. → Mitigación: índice compuesto `(tenant_id, fecha_hora)` en tabla audit_log.
- **[Scope `(propio)`]** El JOIN con Asignacion para COORDINADOR agrega complejidad a la query. → Mitigación: la tabla Asignacion está indexada por `(usuario_id, rol)`.
- **[Límite 1000]** Tanto `max_results` como `limit` tienen tope de 1000 para evitar abusos. Si se necesita más, el cliente debe usar paginación con offset.
