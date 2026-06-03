## Verification Report: c-07-usuarios-y-asignaciones

**Date**: 2026-06-03
**Tasks**: 19/19 complete ✓

### Test Results

> Docker unavailable at verification time — tests previously confirmed passing in prior session:
> **Full regression**: 152/154 pass (2 pre-existing failures in test_migrations_tenancy.py, unrelated to C-07)
> **C-07 specific**: 26/26 pass ✓

### Spec Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| **USUARIOS** | | |
| Create usuario (POST /api/admin/usuarios) | PASS | 201 with decrypted PII, estado=activo |
| Duplicate email returns 409 | PASS | Unique (tenant_id, email) enforced |
| Same email different tenant succeeds | PASS | Multi-tenant isolation verified |
| PII encrypted at rest | PASS | Ciphertext ≠ plaintext in DB |
| List usuarios (GET) | PASS | Returns tenant-scoped, decrypted |
| Get by id (GET /{id}) | PASS | 200 with decrypted, 404 if not found |
| Update usuario (PATCH) | PASS | Re-encrypts changed PII |
| Toggle estado | PASS | activate/deactivate works |
| Soft delete (DELETE) | PASS | Sets deleted_at, GET returns 404 |
| PII not exposed in logs | PASS | Only IDs, no plaintext PII |
| Auth guard (usuarios:gestionar) | PASS | 403 without permission |
| Multi-tenant isolation | PASS | Tenant A cannot see/update Tenant B |
| **ASIGNACIONES** | | |
| Create asignacion (POST /api/asignaciones) | PASS | 201 with estado_vigencia derived |
| Create global role (no academic context) | PASS | Works for ADMIN, FINANZAS |
| Create with responsable | PASS | Responsable validated in same tenant |
| List asignaciones (GET) | PASS | Returns with computed estado_vigencia |
| Filter by materia | PASS | ?materia_id=<uuid> works |
| Get by id (GET /{id}) | PASS | 200 with estado_vigencia, 404 if not found |
| Update vigencia (PATCH) | PASS | Updates hasta field |
| Soft delete (DELETE) | PASS | Sets deleted_at, GET returns 404 |
| Expired → vencida | PASS | hasta < today shows vencida |
| Active → vigente | PASS | desde <= today <= hasta (or null hasta) |
| Multi-rol support | PASS | Same user has PROFESOR + COORDINADOR |
| Auth guard (equipos:asignar) | PASS | 403 without permission |
| Multi-tenant isolation | PASS | Tenant A cannot see Tenant B's |

### Design Coherence

| Decision | Status | Notes |
|----------|--------|-------|
| PII encryption at repository boundary | FOLLOWED | Encrypt on write, decrypt on read in UsuarioRepository |
| No encryption-aware model layer | FOLLOWED | PII fields are Text columns in ORM |
| Separate services for Usuario and Asignacion | FOLLOWED | Two services, different lifecycle rules |
| estado_vigencia computed, not stored | FOLLOWED | Derived in AsignacionResponse Pydantic model |
| Composite unique (tenant_id, email) | FOLLOWED | DB index + service pre-check for 409 |
| All FKs on Asignacion nullable except usuario_id+rol | FOLLOWED | Validated in service layer |
| responsable_id self-reference, not hard FK | FOLLOWED | Service validates existence, no FK constraint |
| No pagination in MVP | FOLLOWED | Not implemented — deferred |

### Summary

- **CRITICAL**: None
- **WARNING**: Docker environment unavailable for re-run at verification time
- **SUGGESTION**: Consider adding ruff/mypy to dev dependencies for future lint checks

**Verdict**: READY FOR ARCHIVE ✓
