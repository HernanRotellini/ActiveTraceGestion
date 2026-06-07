## Context

C-16 incorpora el módulo backend de tareas internas definido por E12/F8/FL-05. El proyecto ya cuenta con la base requerida: tenancy, auth JWT, RBAC, usuarios/asignaciones, estructura académica y módulos de dominio previos. El módulo debe seguir Clean Architecture: Routers → Services → Repositories → Models, con queries solo en repositories, schemas Pydantic v2 `extra='forbid'`, soft delete, `tenant_id` obligatorio e identidad/tenant obtenidos exclusivamente desde la sesión autenticada.

El dominio es de governance MEDIO: impacta lógica operativa de coordinación y docentes, pero no modifica auth, RBAC core ni datos financieros. Aun así, debe ser estricto en permisos, aislamiento tenant y trazabilidad porque las tareas son de alto uso y pueden referenciar contextos académicos.

## Goals / Non-Goals

**Goals:**
- Modelar `Tarea` y `ComentarioTarea` con tenant isolation, soft delete, timestamps y relaciones a `Usuario` y opcionalmente `Materia`.
- Exponer endpoints `/api/tareas/*` para crear, listar, ver detalle, delegar/reasignar, cambiar estado y comentar tareas.
- Soportar “mis tareas” para el usuario autenticado y vista global filtrable para roles con `tareas:gestionar`.
- Validar transiciones de estado y registrar comentarios como hilo cronológico.
- Optimizar consultas de alto uso con índices por tenant, asignado, asignador, materia, estado y fecha.
- Cubrir el módulo con Strict TDD y DB real/efímera.

**Non-Goals:**
- No implementar UI de coordinación ni notificaciones push/email; eso queda para C-23 u otros changes.
- No implementar un motor genérico de workflow configurable; los estados y transiciones de C-16 son explícitos.
- No modificar el catálogo RBAC core salvo usar el permiso esperado `tareas:gestionar` si ya está disponible por seed/matriz.
- No resolver mensajería interna general; C-20 cubre inbox e hilos de mensajes.

## Decisions

### 1. `Tarea` como agregado raíz con `ComentarioTarea` dependiente

`Tarea` será el agregado raíz y `ComentarioTarea` un registro append-like asociado al hilo de la tarea. Las operaciones que cambian estado o delegan pueden incluir comentario opcional para dejar contexto, pero los comentarios nunca reemplazan el estado actual.

Alternativa considerada: usar una tabla genérica de eventos de tarea. Se descarta para MVP porque agrega complejidad y no está pedida por E12; la trazabilidad mínima requerida queda cubierta con `asignado_por`, `asignado_a`, timestamps y comentarios.

### 2. Workflow explícito y fail-closed

Estados permitidos: `Pendiente`, `En progreso`, `Resuelta`, `Cancelada`. Transiciones permitidas: `Pendiente → En progreso`, `Pendiente → Cancelada`, `En progreso → Resuelta`, `En progreso → Cancelada`. Reabrir tareas resueltas/canceladas queda fuera de alcance para evitar ambigüedad de auditoría.

Alternativa considerada: permitir cualquier transición y confiar en UI. Se descarta porque las reglas deben residir server-side y ser testeables.

### 3. Scope de lectura separado entre “mis tareas” y administración global

El endpoint de “mis tareas” lista tareas donde el usuario autenticado sea `asignado_a`. La vista global permite filtros por asignado, asignador, materia, estado y búsqueda libre, pero siempre bajo `tenant_id` del JWT y protegida por `tareas:gestionar`.

Alternativa considerada: un único listado con parámetro `asignado_a=me`. Se descarta para reducir riesgo de suplantación por parámetros y mantener identidad desde sesión.

### 4. Contexto académico opaco opcional

`materia_id` se modela como FK opcional a `Materia`; `contexto_id` queda como UUID opcional opaco para vincular tareas a otra entidad del dominio cuando el frontend lo necesite. El backend no infiere permisos desde `contexto_id` en este change; solo conserva la referencia.

Alternativa considerada: múltiples FKs por tipo de contexto. Se descarta por ampliar demasiado el alcance y acoplar C-16 a todos los módulos.

### 5. Índices orientados a alto uso

La migración debe crear índices compuestos sobre `(tenant_id, asignado_a, estado)`, `(tenant_id, asignado_por)`, `(tenant_id, materia_id)`, `(tenant_id, estado)` y un orden por fecha de creación/actualización para listados frecuentes.

Alternativa considerada: índices mínimos solo por FK. Se descarta porque FL-05 advierte cientos de tareas simultáneas y F8.3 requiere filtros globales.

## Risks / Trade-offs

- [Permisos demasiado amplios] `tareas:gestionar` puede permitir ver más de lo deseado si la matriz RBAC no distingue propio/global → Mitigación: separar endpoints de “mis tareas” vs global y documentar tests de acceso.
- [Contexto opaco sin integridad referencial] `contexto_id` no valida existencia de la entidad referenciada → Mitigación: mantenerlo opcional/opaco en C-16 y validar solo `materia_id`; futuras capacidades pueden especializarlo.
- [Volumen de comentarios] Hilos largos pueden afectar detalle de tarea → Mitigación: cargar comentarios ordenados y paginables o limitar por defecto si el patrón del repo ya contempla paginación.
- [Auditoría no disponible/pendiente] C-05 puede no estar aplicado aunque la KB pide auditoría para acciones significativas → Mitigación: no bloquear C-16; si existe helper de audit, registrar alta/delegación/cambio de estado, si no, dejar integración preparada para un change posterior.

## Migration Plan

1. Crear migración Alembic dedicada para `tarea` y `comentario_tarea` con FKs, enums/constraints, soft delete e índices.
2. Implementar modelos SQLAlchemy y repositories tenant-scoped.
3. Implementar schemas Pydantic, service con reglas de transición y router con guards.
4. Ejecutar tests TDD con PostgreSQL real/efímero.
5. Rollback: eliminar tablas/índices/enums creados por la migración si no hay datos productivos; en producción, respaldar antes de downgrade.

## Open Questions

- ¿El permiso `tareas:gestionar` ya está seedado en la matriz RBAC de C-04 o debe agregarse en la migración/seed de este change?
- ¿La vista “mis tareas” debe permitir a cualquier usuario con sesión leer sus tareas aunque no tenga `tareas:gestionar`, o el permiso debe ser obligatorio para todo `/api/tareas/*` como indica CHANGES.md? Para este change se asume permiso obligatorio en todos los endpoints.
