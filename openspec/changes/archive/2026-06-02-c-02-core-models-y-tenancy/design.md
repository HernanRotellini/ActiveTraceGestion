## Context

`c-02-core-models-y-tenancy` es el primer change crítico después del cimiento técnico. C-01 dejó el esqueleto FastAPI/SQLAlchemy/Alembic; ahora se debe establecer el contrato transversal que todos los módulos posteriores heredarán: tenant como raíz, UUID interno, timestamps, soft delete, repositories tenant-scoped y cifrado AES-256 para PII/secrets.

La decisión ADR-002 ya está cerrada: multi-tenancy row-level con una sola base PostgreSQL, columna `tenant_id` en toda tabla de dominio y filtro automático en cada repository. Cambiar esto después impactaría cada tabla, request y módulo, por lo que este change debe diseñarse con tests de regresión fuertes desde el inicio.

## Goals / Non-Goals

**Goals:**
- Crear el modelo `Tenant` y una base ORM reutilizable para entidades con UUID, timestamps y soft delete.
- Definir el patrón repository base async que requiere `tenant_id` explícito y aplica scope por defecto en cada query tenant-scoped.
- Garantizar que los registros soft-deleted no aparezcan en operaciones normales.
- Incorporar cifrado/descifrado AES-256 para valores sensibles en reposo con configuración vía `ENCRYPTION_KEY`.
- Entregar migración Alembic inicial y tests TDD de aislamiento, soft delete, timestamps y cifrado round-trip.

**Non-Goals:**
- Implementar autenticación JWT, resolución real de usuario actual o RBAC; eso pertenece a C-03/C-04.
- Crear entidades académicas (`Carrera`, `Cohorte`, `Materia`, `Dictado`) o usuarios; eso pertenece a changes posteriores.
- Implementar audit log append-only; este cimiento solo preserva histórico con soft delete.
- Resolver permisos o excepciones de acceso cross-tenant para administración global; el sistema debe fallar cerrado.

## Decisions

1. **Tenant row-level como contrato de repository, no como convención informal.**
   - Decisión: todo repository tenant-scoped se construye con `tenant_id` y aplica `WHERE model.tenant_id == tenant_id` en list/get/update/soft_delete por defecto.
   - Alternativa considerada: confiar en que cada query agregue el filtro manualmente. Se descarta porque un olvido sería una fuga de datos entre instituciones.
   - Rationale: hace testeable la regla dura “un query sin scope de tenant es un bug”.

2. **Base mixin separa entidades globales de entidades tenant-scoped.**
   - Decisión: usar un mixin común para UUID/timestamps/soft delete y otro para `tenant_id`; `Tenant` no se referencia a sí mismo, pero las tablas de dominio futuras sí usan el mixin tenant-scoped.
   - Alternativa considerada: meter `tenant_id` en una única base universal. Se descarta porque `Tenant` y posibles tablas técnicas globales no deben tenerlo.
   - Rationale: evita excepciones raras en el modelo raíz sin debilitar la regla para dominio.

3. **Soft delete por timestamp (`deleted_at`) y exclusión por defecto.**
   - Decisión: `soft_delete()` marca `deleted_at`; las operaciones normales excluyen `deleted_at IS NOT NULL`.
   - Alternativa considerada: columna booleana `is_deleted`. Se descarta porque el timestamp aporta trazabilidad temporal y reduce ambigüedad.
   - Rationale: preserva histórico y prepara el camino para auditabilidad sin hard delete.

4. **Cifrado AES-256 centralizado y explícito.**
   - Decisión: exponer helpers puros de cifrado/descifrado en core, alimentados por `ENCRYPTION_KEY` validada como clave de 32 bytes, y usarlos desde modelos/repositorios/servicios que manejen PII en changes posteriores.
   - Alternativa considerada: cifrado automático transparente en tipos SQLAlchemy desde el inicio. Se posterga porque todavía no existen las entidades PII; un helper explícito permite testear el contrato ahora y especializar tipos después si conviene.
   - Rationale: evita texto plano en reposo y mantiene bajo acoplamiento en el cimiento.

5. **Tests con PostgreSQL real/efímero, sin mocks de DB.**
   - Decisión: las pruebas de repositories/modelos se ejecutan contra la base de test configurada, usando transacciones/fixtures para aislamiento.
   - Alternativa considerada: mocks de SQLAlchemy/session. Se descarta por regla dura del proyecto: no prueban aislamiento real ni SQL generado.
   - Rationale: el objetivo del change es precisamente validar comportamiento de persistencia.

## Risks / Trade-offs

- **Riesgo: una entidad futura omite el mixin tenant-scoped.** → Mitigación: documentar patrón y agregar tests/fixtures que fallen si un repository tenant-scoped opera sobre modelo sin `tenant_id`.
- **Riesgo: bypass por uso directo de session fuera de repositories.** → Mitigación: mantener regla arquitectónica Routers → Services → Repositories y cubrir en review; los services no emiten SQL.
- **Riesgo: cifrado no determinístico dificulta búsquedas por PII.** → Mitigación: este change solo exige round-trip y reposo cifrado; búsquedas sobre PII deberán diseñarse explícitamente cuando se implementen usuarios.
- **Riesgo: migración temprana condiciona todos los changes siguientes.** → Mitigación: mantener schema mínimo (`tenants`) y mixins en código, sin adelantar entidades de dominio.

## Migration Plan

1. Crear migración Alembic inicial para tabla `tenants` con UUID, nombre/código/estado básico si aplica, timestamps y soft delete.
2. Aplicar migración en entorno local/test antes de ejecutar tests de repository.
3. Validar que rollback elimina solo la tabla nueva y no toca infraestructura de C-01.
4. No hay migración de datos existente porque el producto aún está en etapa fundacional.

## Open Questions

- Ninguna bloqueante para C-02. Las preguntas abiertas sobre estructura académica, NEXO y liquidaciones no afectan este cimiento.
