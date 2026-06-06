## Context

El sistema actualmente carece de un canal de comunicación institucional interna (tablón de avisos). Las únicas comunicaciones salientes son los emails a alumnos (C-12). Los COORDINADORES y ADMIN necesitan publicar novedades, alertas y recordatorios visibles dentro de la plataforma, con control de alcance (por rol, materia, cohorte o global), vigencia programada y confirmación de lectura obligatoria.

Este cambio se apoya en la infraestructura existente:
- **C-06** (estructura académica): entidades `Materia`, `Carrera`, `Cohorte` como contexto de alcance
- **C-04** (RBAC): permisos finos `modulo:accion` — se agrega `avisos:publicar`
- **C-02** (core-models): mixin con `tenant_id`, UUID, soft delete, timestamps
- **C-05** (audit-log): registro de acciones significativas (cuando esté disponible)

## Goals / Non-Goals

**Goals:**
- ABM completo de avisos con alcance configurable (Global / PorMateria / PorCohorte / PorRol)
- Visualización automática filtrada: cada usuario ve solo los avisos que le corresponden según su rol, materia asignada y cohorte
- Confirmación de lectura (acknowledgment) opcional por aviso
- Contadores derivados de `AcknowledgmentAviso` (no denormalizados)
- Ventana de vigencia programada: `inicio_en` / `fin_en`
- Orden de prioridad configurable para presentación
- Severidad: Info / Advertencia / Crítico
- Auditoría de operaciones CRUD sobre avisos

**Non-Goals:**
- Notificaciones push ni emails al crear/publicar un aviso (la visibilidad es bajo demanda en la plataforma)
- Avisos recurrentes o automatizados (todos son creados manualmente)
- Avisos con adjuntos o archivos multimedia
- Traducción multi-idioma del contenido

## Decisions

### 1. Modelo único `Aviso` con campo `alcance` enum
- **Decisión**: Un solo modelo `Aviso` con campo `alcance` (`Global | PorMateria | PorCohorte | PorRol`) y campos opcionales `materia_id`, `cohorte_id`, `rol_destino`.
- **Alternativa descartada**: modelo polimórfico con tablas separadas por alcance. Descartado por sobreingeniería — las columnas nullable son suficientes y la lógica de filtrado es simple.
- **Justificación**: el alcance se resuelve con una condición `WHERE` en el repository, no requiere joins complejos ni tablas extra.

### 2. Filtrado de visibilidad en el repository, no en service
- **Decisión**: la lógica de qué avisos ve un usuario se resuelve en el repository mediante condiciones parametrizadas (usuario_id, roles, materias_asignadas, cohortes_asignadas).
- **Justificación**: evita traer todos los avisos del tenant a memoria para filtrar en Python. El repository construye dinámicamente la cláusula `WHERE` según el perfil del usuario.

### 3. Contadores derivados de `AcknowledgmentAviso`
- **Decisión**: no hay campos `total_vistas`, `total_acks` en `Aviso`. Se calculan con `COUNT(*)` sobre `AcknowledgmentAviso` agrupado por `aviso_id`.
- **Justificación**: consistencia con la regla de negocio RN-20 (contadores derivados). La carga de consulta es baja (< 100 avisos activos por tenant).

### 4. Soft delete con `activo` booleano + borrado físico protegido
- **Decisión**: `Aviso` tiene campo `activo` booleano. Un aviso inactivo no se muestra. El borrado físico solo ocurre vía ADMIN y genera audit log.
- **Alternativa descartada**: soft delete completo con `deleted_at`. Descartado porque el modelo ya tiene vigencia programada — `activo` es más simple para casos donde se quiere "despublicar" sin borrar.

### 5. Permiso `avisos:publicar` en lugar de reusar `estructura:gestionar`
- **Decisión**: permiso específico `avisos:publicar` en la matriz RBAC.
- **Justificación**: los avisos son una capacidad distinta de la gestión de estructura académica. Un COORDINADOR puede necesitar publicar avisos sin necesariamente gestionar carreras/materias.

### 6. Un único endpoint público vs dos rutas separadas
- **Decisión**: un solo endpoint `GET /api/avisos` que filtra según el usuario autenticado. Endpoint separado `GET /api/admin/avisos` para gestión (CRUD).
- **Justificación**: separación clara entre "lo que ve el usuario" vs "lo que administra el publicador". El endpoint público es de solo lectura y aplica filtros automáticos.

### 7. `AcknowledgmentAviso` usa `(aviso_id, usuario_id)` como unique constraint
- **Decisión**: un usuario puede confirmar un aviso una sola vez. El unique constraint previene duplicados.
- **Justificación**: consistencia con la semántica de "ya leído/confirmado".

## API Design

### Endpoints públicos (autenticado)

| Método | Ruta | Permiso | Descripción |
|--------|------|---------|-------------|
| `GET` | `/api/avisos` | `autenticado` | Lista avisos visibles para el usuario actual (filtrados por alcance, rol, vigencia, activo). Ordenados por `orden` ASC, `inicio_en` DESC. |
| `POST` | `/api/avisos/{id}/ack` | `autenticado` | Confirma lectura del aviso. Crea `AcknowledgmentAviso`. Idempotente (segundo POST es no-op). |
| `GET` | `/api/avisos/pendientes-ack` | `autenticado` | Lista avisos visibles que requieren ack y no han sido confirmados por el usuario actual. |

### Endpoints de gestión (COORDINADOR/ADMIN)

| Método | Ruta | Permiso | Descripción |
|--------|------|---------|-------------|
| `GET` | `/api/admin/avisos` | `avisos:publicar` | Lista todos los avisos del tenant (incluyendo inactivos y fuera de vigencia). |
| `POST` | `/api/admin/avisos` | `avisos:publicar` | Crea un nuevo aviso. |
| `GET` | `/api/admin/avisos/{id}` | `avisos:publicar` | Detalle de un aviso. |
| `PUT` | `/api/admin/avisos/{id}` | `avisos:publicar` | Modifica un aviso. |
| `DELETE` | `/api/admin/avisos/{id}` | `avisos:publicar` | Desactiva/elimina un aviso (soft delete: `activo = false`). |
| `GET` | `/api/admin/avisos/{id}/stats` | `avisos:publicar` | Estadísticas del aviso: total_acks, acks por día, usuarios sin confirmar. |

## Data Model

### `Aviso`
```
id              : UUID       — PK
tenant_id       : UUID       — FK → Tenant
alcance         : enum       — Global | PorMateria | PorCohorte | PorRol
materia_id      : UUID       — FK → Materia (nullable)
cohorte_id      : UUID       — FK → Cohorte (nullable)
rol_destino     : enum       — rol destinatario (nullable = todos los roles)
severidad       : enum       — Info | Advertencia | Crítico (default: Info)
titulo          : string(200)
cuerpo          : text       — contenido enriquecido (Markdown o HTML sanitizado)
inicio_en       : datetime   — desde cuándo es visible
fin_en          : datetime   — hasta cuándo es visible (nullable = sin límite)
orden           : integer    — prioridad de presentación (menor = primero, default: 0)
activo          : boolean    — si está publicado (default: true)
requiere_ack    : boolean    — si requiere confirmación de lectura (default: false)
created_at      : datetime   — mixin
updated_at      : datetime   — mixin
deleted_at      : datetime   — mixin (soft delete)
```

### `AcknowledgmentAviso`
```
id              : UUID       — PK
aviso_id        : UUID       — FK → Aviso
usuario_id      : UUID       — FK → Usuario
confirmado_at   : datetime   — timestamp de confirmación
tenant_id       : UUID       — FK → Tenant
```

**Unique constraint**: `(aviso_id, usuario_id)`

## Service Layer

### `AvisoService`

| Método | Descripción |
|--------|-------------|
| `listar_visibles(usuario, roles, materias_ids, cohortes_ids)` | Retorna avisos visibles filtrados por perfil |
| `listar_admin(tenant_id, filtros)` | Lista admin con filtros (alcance, severidad, activo, rango fechas) |
| `crear(datos)` | Crea aviso + audit log |
| `actualizar(id, datos)` | Actualiza aviso + audit log |
| `desactivar(id)` | Soft delete (activo=false) + audit log |
| `confirmar_lectura(aviso_id, usuario_id)` | Crea ack (idempotente) + audit log |
| `obtener_stats(aviso_id)` | Contadores de ack |

### Lógica de visibilidad (en repository)

```
WHERE a.tenant_id = :tenant_id
  AND a.activo = true
  AND a.inicio_en <= NOW()
  AND (a.fin_en IS NULL OR a.fin_en >= NOW())
  AND (
    a.alcance = 'Global'
    OR (a.alcance = 'PorRol' AND a.rol_destino IN (:roles_usuario))
    OR (a.alcance = 'PorMateria' AND a.materia_id IN (:materias_usuario))
    OR (a.alcance = 'PorCohorte' AND a.cohorte_id IN (:cohortes_usuario))
  )
ORDER BY a.orden ASC, a.inicio_en DESC
```

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| [Rendimiento] Muchos avisos activos con alcance PorMateria requieren pasar lista de materias del usuario | Las listas de materias del usuario rara vez superan 10-15 items. Índice compuesto en `(tenant_id, activo, inicio_en, alcance)`. |
| [Consistencia] Un aviso con `alcance=PorMateria` pero sin `materia_id` por error | Validación en schema Pydantic: si alcance es PorMateria o PorCohorte, el id correspondiente es requerido. |
| [Auditoría] Operaciones CRUD sin audit log (si C-05 no está implementado aún) | El service registra audit via `AuditLogRepository.create()` si el módulo existe; si no, queda como stub. El permiso `avisos:publicar` ya está disponible desde C-04. |
| [SQL Injection] Filtros dinámicos en repository | Uso exclusivo de SQLAlchemy ORM con bind params. Nunca concatenación de strings. |

## Migration Plan

1. Crear migración Alembic con tablas `aviso` y `acknowledgment_aviso`
2. Agregar permiso `avisos:publicar` al seed de RBAC (roles COORDINADOR, ADMIN)
3. Implementar modelos → schemas → repositorio → servicio → router (orden ascendente)
4. Tests unitarios y de integración
5. Rollback: `alembic downgrade -1` y remover permiso del seed

## Open Questions

- ¿El cuerpo del aviso debe soportar HTML enriquecido o solo Markdown? → **Decisión temprana**: Markdown sanitizado, se renderiza en frontend. Si se necesita HTML, se evalúa en C-23 (frontend).
- ¿Los avisos con `alcance=PorRol` y `rol_destino=ALUMNO` deben filtrar además por materia/cohorte? → Por ahora no — si es PorRol + ALUMNO, se muestra a TODOS los alumnos del tenant. Si se necesita acotar, se usa `PorMateria` o `PorCohorte`.
