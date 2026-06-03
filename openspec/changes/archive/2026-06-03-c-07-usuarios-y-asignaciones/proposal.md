## Why

The academic management workflow requires managing the people who operate the system — docentes, coordinadores, tutores — and their assignments to academic contexts. Without a dedicated user identity model with PII protection and a flexible assignment system (Usuario ↔ Rol ↔ Carrera/Cohorte/Materia), no team can be configured, no communication can be targeted, and no liquidations can be calculated. C-07 builds the user registry and assignment engine — the foundational layer for all downstream people-centric features (equipos docentes, comunicaciones, liquidaciones).

## What Changes

- **New model `Usuario`**: tenant-scoped identity with **AES-256 encrypted PII** (email, dni, cuil, cbu, alias_cbu); legajo as optional business attribute (not PK, not credential); estado Activo/Inactivo; unique `(tenant_id, email)`
- **New model `Asignacion`**: links Usuario ↔ Rol ↔ academic context (carrera/cohorte/materia/comisiones) with `responsable_id` hierarchy, vigencia `desde/hasta`, and derived `estado_vigencia`
- **New migration 005**: creates `usuarios` and `asignaciones` tables with composite unique indexes
- **New service layer**: `UsuarioService` (ABM with PII encryption/decryption transparent to callers) and `AsignacionService` (CRUD + vigencia validation)
- **New REST endpoints**: `/api/admin/usuarios` (ADMIN, guard `usuarios:gestionar`) and `/api/asignaciones` (COORDINADOR/ADMIN, guard `equipos:asignar`)
- **PII never exposed**: encrypted fields are automatically decrypted only in service responses; never logged in plaintext
- **Vigencia rules**: expired assignment does not grant permissions but is kept as historical record
- **Multi-rol support**: a user can have multiple assignments with different roles and contexts simultaneously
- **Tests**: PII encryption round-trip (not exposed in logs/responses), email uniqueness per tenant, vigencia expiration, multi-rol, hierarchy responsable, multi-tenant isolation

## Capabilities

### New Capabilities
- `usuarios`: ABM for Usuario with automatic AES-256 encryption of PII fields, email uniqueness per tenant, state management
- `asignaciones`: CRUD for Asignacion (Usuario ↔ Rol ↔ context) with vigencia temporal, responsable hierarchy, and derived estado_vigencia

### Modified Capabilities
- (none — first user/assignment capability)

## Impact

- **Backend**: new models `usuarios_asignaciones.py`; new schemas `usuarios.py`, `asignaciones.py`; new repositories `usuarios.py`, `asignaciones.py`; new services `usuarios.py`, `asignaciones.py`; new routers `usuarios.py`, `asignaciones.py`; wire into app router registry
- **Permissions**: `USUARIOS_GESTIONAR` and `EQUIPOS_ASIGNAR` already exist as constants in `permisos.py` — no new constants needed
- **Database**: migration 005 with 2 new tables, composite unique indexes, FKs to usuarios, roles, carreras, cohortes, materias
- **Tests**: new suite `tests/test_usuarios.py`, `tests/test_asignaciones.py`
