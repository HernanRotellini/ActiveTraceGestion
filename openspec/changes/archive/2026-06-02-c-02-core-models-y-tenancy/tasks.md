## 1. Safety Net y Preparación TDD

- [x] 1.1 Ejecutar la suite existente relevante de backend/modelos/repositorios para capturar baseline antes de modificar archivos existentes.
- [x] 1.2 Identificar fixtures de PostgreSQL real/efímero disponibles y confirmar que no se usen mocks de DB.
- [x] 1.3 Crear primero tests RED para `Tenant` y mixins base: UUID, timestamps y ausencia de `tenant_id` en `Tenant`.

## 2. Tenant y Base ORM

- [x] 2.1 Implementar el modelo `Tenant` mínimo con UUID interno, campos de identificación, timestamps y soft delete.
- [x] 2.2 Implementar mixins/base ORM reutilizables para UUID, timestamps, soft delete y `tenant_id` en entidades tenant-scoped.
- [x] 2.3 Triangular tests de timestamps: creación, actualización y estabilidad de `created_at`.

## 3. Repository Base Tenant-Scoped

- [x] 3.1 Escribir tests RED de aislamiento multi-tenant: list/get no devuelven registros de otro tenant.
- [x] 3.2 Implementar repository base async que exige `tenant_id` y aplica scope por defecto.
- [x] 3.3 Escribir tests RED para fail-closed cuando falta tenant context.
- [x] 3.4 Implementar validación de tenant context y rechazo de operaciones unscoped.

## 4. Soft Delete Transversal

- [x] 4.1 Escribir tests RED para soft delete: marcar `deleted_at`, ocultar en lecturas normales y evitar hard delete.
- [x] 4.2 Implementar `soft_delete` en repository/base model y exclusión por defecto de `deleted_at IS NOT NULL`.
- [x] 4.3 Triangular con casos get/list después de delete y cross-tenant después de delete.

## 5. Cifrado AES-256 en Reposo

- [x] 5.1 Escribir tests RED de cifrado round-trip, ciphertext distinto del plaintext y validación de clave.
- [x] 5.2 Implementar helper centralizado de cifrado/descifrado usando `ENCRYPTION_KEY` validada.
- [x] 5.3 Escribir tests RED para errores sin filtración de plaintext/ciphertext sensible.
- [x] 5.4 Ajustar manejo de errores del helper para fallar cerrado sin exponer valores sensibles.

## 6. Migración Alembic y Verificación

- [x] 6.1 Escribir/verificar test de migración sobre DB de test para creación de tabla `tenants`.
- [x] 6.2 Crear migración Alembic inicial de tenant foundation y rollback scoped.
- [x] 6.3 Ejecutar tests del change y registrar evidencia Strict TDD: safety net, RED, GREEN, triangulación y refactor.
- [x] 6.4 Revisar que ningún archivo backend supere 500 LOC y que el patrón Routers → Services → Repositories → Models quede preservado.
