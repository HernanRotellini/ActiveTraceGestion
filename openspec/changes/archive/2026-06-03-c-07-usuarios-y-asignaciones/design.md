## Context

C-07 builds the user identity and assignment layer on top of the existing infrastructure: tenant-scoped models (C-01/C-02), JWT authentication (C-03), RBAC with fine-grained permissions (C-04), and the academic catalog of carreras/cohortes/materias (C-06). AES-256 encryption helpers already exist in `core/encryption.py` and the `ENCRYPTION_KEY` config is already wired. The permissions `USUARIOS_GESTIONAR` and `EQUIPOS_ASIGNAR` already exist as constants in `permisos.py`.

The key architectural challenge is transparent PII encryption: store encrypted values at rest, decrypt automatically when reading via the service layer, but never expose plaintext in logs, error messages, or raw repository output.

## Goals / Non-Goals

**Goals:**
- Provide ABM for Usuario with automatic AES-256 encryption of PII fields (email, dni, cuil, cbu, alias_cbu) — encryption is transparent to the API consumer but enforced at the repository/service boundary
- Enforce unique `(tenant_id, email)` at DB and service layer
- Provide CRUD for Asignacion (Usuario ↔ Rol ↔ academic context) with vigencia `desde/hasta`, `responsable_id` hierarchy, and derived `estado_vigencia`
- Expired assignments are kept as historical records but do not grant permissions
- Multi-rol support: a user can hold multiple assignments with different roles in different contexts
- Full multi-tenant isolation on both entities

**Non-Goals:**
- Frontend UI (API-only change)
- Assignment of ALUMNO role (padrón mass import is C-09)
- Assignment cloning between periods (C-08 equipos-docentes)
- Impersonation flows (C-05 audit-log)

## Decisions

1. **PII encryption at the repository write/read boundary** — the repository layer automatically encrypts PII fields on write (create/update) and decrypts on read (get/list). This keeps encryption concerns in one place and prevents callers from accidentally storing plaintext. The service layer works with plaintext values; the repository transparently handles ciphertext.

2. **No encryption-aware model layer** — PII fields are stored as plaintext `Text` columns in the ORM (the column type is not the security boundary). Encryption is enforced at the repository layer, never at the model. This avoids coupling SQLAlchemy to the encryption module and keeps models simple.

3. **Separate services for Usuario and Asignacion** — despite being related entities, their lifecycle and business rules differ enough to warrant separate services. `UsuarioService` handles identity lifecycle (create, update, activate/deactivate, PII updates); `AsignacionService` handles role-context linking (assign, revoke, filter by vigencia).

4. **Derived `estado_vigencia` computed at service layer** — following the KB spec, `estado_vigencia` is not stored. It is computed on read by comparing `desde`/`hasta` against the current date. This avoids stale computed columns.

5. **Composite unique index on `(tenant_id, email)` for usuarios** — enforces the domain rule that email is unique per tenant at the database level, with a pre-check in the service layer for a clean 409 response.

6. **Foreign keys on Asignacion are all nullable** — an assignment may be tenant-global (ADMIN, FINANZAS roles) with no academic context, or scoped to carrera-level only (COORDINADOR without materia). Only `usuario_id` and `rol` are required. Validation of sufficient context is a business rule in the service.

7. **`responsable_id` is a self-reference to Usuario** — models reporting hierarchy. Validated at service creation to ensure the responsable exists in the same tenant. Not a hard FK to avoid cycles (the hierarchy is soft).

8. **No pagination in MVP** — both Usuario and Asignacion lists are expected to be small (tens to low hundreds per tenant). Pagination can be added in a later change.

## Risks / Trade-offs

- [Risk] PII could accidentally be logged in plaintext during service operations → [Mitigation] the encryption boundary is at the repository; logs in services use only user IDs, never PII fields; a dedicated test asserts ciphertext ≠ plaintext in DB
- [Risk] Decryption failure could expose partial data → [Mitigation] `decrypt_sensitive_value` raises `EncryptionError` without leaking plaintext; the service catches it and returns a generic error
- [Risk] Expired assignments (vigencia vencida) could be confused in list views → [Mitigation] list endpoints return all assignments with computed `estado_vigencia`; consumers filter as needed; a query parameter `?solo_vigentes=true` can be added later
- [Risk] `responsable_id` cycles could cause infinite loops in hierarchy → [Mitigation] no recursive queries in MVP; the hierarchy is flat (one level: responsable → asignado)
