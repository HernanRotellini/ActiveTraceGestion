## Why

El sistema necesita fijar el cimiento multi-tenant antes de implementar autenticación, RBAC o cualquier módulo de dominio: cada dato debe pertenecer a una institución y ninguna consulta puede cruzar tenants. Este change convierte las reglas fundacionales de persistencia —Tenant raíz, scope por tenant, soft delete y cifrado en reposo— en contratos implementables y testeables.

## What Changes

- Introducir el modelo raíz `Tenant` y mixins/base ORM compartidos con UUID interno, `tenant_id`, timestamps y `deleted_at` para soft delete.
- Crear un repository base async con scope de tenant obligatorio por defecto para lecturas/escrituras, excluyendo registros soft-deleted salvo intención explícita.
- Agregar helper transversal de cifrado/descifrado AES-256 para atributos sensibles marcados como `[cifrado]`, evitando exposición accidental en logs o texto plano.
- Configurar Alembic para la primera migración de schema del dominio (`tenant`) y documentar la convención de una migración por cambio de schema.
- Cubrir con tests de aislamiento multi-tenant, soft delete, timestamps y cifrado round-trip usando base real/efímera, sin mocks de DB.

## Capabilities

### New Capabilities
- `tenant-isolation`: Contratos para `Tenant`, entidades tenant-scoped, repositories con filtro obligatorio por `tenant_id`, soft delete transversal y garantías de no cruce de datos entre instituciones.
- `data-encryption-at-rest`: Contratos para cifrado/descifrado AES-256 de PII/secrets en reposo y prevención de exposición accidental de valores sensibles.

### Modified Capabilities
- Ninguna.

## Impact

- Backend: `backend/app/models/`, `backend/app/repositories/`, `backend/app/core/tenancy.py`, `backend/app/core/security.py` o módulo equivalente de cifrado, y dependencias de sesión/tenant existentes.
- Base de datos: primera migración Alembic de `Tenant` y columnas/base mixin para futuras tablas tenant-scoped.
- Tests: suite pytest de repositories/modelos/cifrado con PostgreSQL real o contenedor de test; no se aceptan mocks de DB.
- Seguridad/arquitectura: cambio CRÍTICO porque define aislamiento de tenant, soft delete y cifrado en reposo para el resto del producto.
