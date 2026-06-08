# Verify Report — C-09: Padrón / Ingesta Moodle

**Date**: 2026-06-07
**Tests run**: `cd backend; python -m pytest tests/test_padron.py -v`

---

## Test Results

| Result | Count |
|--------|-------|
| **PASSED** | 9 |
| **ERROR (setup)** | 12 |
| **FAILED** | 0 |
| **Total** | 21 |

### Passed tests (9)

| Test | Layer |
|------|-------|
| `TestFileParser::test_csv_valid_parsing` | Unit |
| `TestFileParser::test_csv_semicolon_delimiter` | Unit |
| `TestFileParser::test_csv_missing_required_columns` | Unit |
| `TestFileParser::test_csv_empty_file` | Unit |
| `TestFileParser::test_csv_skips_empty_rows` | Unit |
| `TestFileParser::test_csv_preview_limited` | Unit |
| `TestFileParser::test_unsupported_format` | Unit |
| `TestMoodleClient::test_not_configured_raises_error` | Unit |
| `TestMoodleClient::test_configured_returns_true` | Unit |

### Errored tests (12) — all `ConnectionDoesNotExistError`

All DB-dependent tests error because PostgreSQL is **not running** on `localhost:5432`. This is a pre-existing infrastructure issue, not a code defect.

| Test | Layer | Root cause |
|------|-------|------------|
| `TestVersionPadronModel` (4 tests) | Integration | DB unavailable |
| `TestPadronRepository` (2 tests) | Integration | DB unavailable |
| `TestImportFlow` (4 tests) | E2E via HTTP | DB unavailable |
| `TestVaciar` (1 test) | E2E via HTTP | DB unavailable |
| `TestMoodleSync` (1 test) | E2E via HTTP | DB unavailable |

---

## Requirement Coverage (per spec scenarios)

### Spec: padron-ingesta

| # | Scenario | Covered by test | Status |
|---|----------|----------------|--------|
| R1 | Create first version activates it | `test_create_first_version_activates_it` | 🟡 DB error |
| R1 | Second import deactivates first | `test_second_version_deactivates_first` | 🟡 DB error |
| R1 | Version history preserved (3 versions) | `test_three_versions_only_latest_active` | 🟡 DB error |
| R2 | EntradaPadron without usuario_id | `test_entrada_padron_without_usuario_id` | 🟡 DB error |
| R2 | Email encrypted at rest | ❌ **Not tested** | 🔴 Gap |
| R3 | Successful xlsx/csv import with preview | `test_preview_returns_column_info` | 🟡 DB error |
| R3 | Preview token used for confirmation | `test_confirm_creates_version` | 🟡 DB error |
| R3 | Preview token expired → 409 | `test_confirm_with_expired_token_returns_409` | 🟡 DB error |
| R3 | CSV with semicolon delimiter | `test_csv_semicolon_delimiter` | ✅ Pass |
| R3 | Malformed file → descriptive error | `test_csv_missing_required_columns`, `test_csv_empty_file` | ✅ Pass |
| R4 | Teacher clears own data | `test_vaciar_removes_own_versions` | 🟡 DB error |
| R4 | Other teacher's data preserved | `test_vaciar_only_own_data` | 🟡 DB error |
| R5 | Import generates audit entry | ❌ **Not tested** | 🔴 Gap |
| R5 | Vaciar generates audit entry | ❌ **Not tested** | 🔴 Gap |
| R6 | Tenant isolation on query | ❌ **Not tested** | 🔴 Gap |

### Spec: moodle-integracion

| # | Scenario | Covered by test | Status |
|---|----------|----------------|--------|
| R1 | Sync users from Moodle course | ❌ **Not tested** (no mock HTTP) | 🔴 Gap |
| R1 | Moodle WS unavailable → 502 | `test_sync_without_moodle_config_returns_502` | 🟡 DB error |
| R2 | Teacher triggers on-demand sync | ❌ **Not tested** | 🔴 Gap |
| R2 | Unauthorized user → 403 | ❌ **Not tested** | 🔴 Gap |
| R3 | Nightly sync (scheduled) | ❌ **Not tested** | 🔴 Gap |
| R4 | No Moodle config → manual import | `test_not_configured_raises_error` | ✅ Pass |
| R5 | Transient error retries | ❌ **Not tested** | 🔴 Gap |
| R5 | Auth failure immediate | ❌ **Not tested** | 🔴 Gap |

---

## Design Decision Verification (per design.md)

| D# | Decision | Evidence in code | Status |
|----|----------|------------------|--------|
| D1 | Versionado explícito con activación manual | `VersionPadronRepository.crear_version()` desactiva versión previa en misma transacción | 🟡 DB error |
| D2 | Preview como paso previo a confirmación | Endpoints `POST /api/v1/padron/preview` + `POST /api/v1/padron/confirmar` | 🟡 DB error |
| D3 | MoodleClient como integration aislada | `app/integrations/moodle_ws.py` con `MoodleClient`, `MoodleConfig` | ✅ Verified |
| D4 | Vaciado con scope `(usuario_id, materia_id)` | `EntradaPadronRepository.vaciar_por_usuario_y_materia()` | 🟡 DB error |
| D5 | Email cifrado AES-256 | No hay test que verifique ciphertext en DB | 🔴 Gap |

---

## Task Completion (per tasks.md)

| Task | Status | Notes |
|------|--------|-------|
| 1.1-1.3: Modelos y migración | 🟢 Models exist | `app/models/padron.py`, migration exists |
| 2.1-2.2: Schemas Pydantic | 🟢 Schemas exist | `app/schemas/padron.py`, `ImportPreviewResponse`, etc. |
| 3.1-3.2: Repositorio | 🟢 Repo exists | `app/repositories/padron.py` with `VersionPadronRepository`, `EntradaPadronRepository` |
| 4.1: File parser | 🟢 Implemented | `app/services/file_parser.py`, 7 tests pass |
| 5.1: Preview cache | 🟢 Implemented | In-memory cache with TTL 30min |
| 6.1: PadronService | 🟢 Service exists | `app/services/padron.py` |
| 7.1-7.2: Router Padrón | 🟢 Router exists | `app/api/v1/routers/padron.py`, registered in main |
| 8.1-8.2: MoodleClient | 🟢 Implemented | `app/integrations/moodle_ws.py` |
| 9.1-9.3: Moodle Sync | 🟢 Router exists | `app/api/v1/routers/moodle.py` |
| 10.1-10.2: Main integration | 🟢 Confirmed | Routers registered in `main.py` |
| 11.1-11.7: Tests | 🟡 Partial | 7/7 unit tests pass; 0/12 integration tests runnable (DB down) |

---

## Gaps Found

### 🔴 Gap 1: Email encryption not tested
Spec requires "Email is encrypted at rest" (verify ciphertext via direct DB query). No test asserts this. Implied by reuse of `app/core/encryption.py` but not verified.

### 🔴 Gap 2: Audit trail not tested
Two spec scenarios require audit entries (`PADRON_CARGAR` on import and vaciar). No test asserts audit log creation.

### 🔴 Gap 3: Tenant isolation not tested
Spec requires tenant-scoped queries. No test asserts cross-tenant isolation.

### 🔴 Gap 4: Moodle WS HTTP tests absent
No mock HTTP tests for `MoodleClient.sync_usuarios()` — retry logic, auth failure, success path rely on manual verification only.

### 🟡 Gap 5: DB unavailable
PostgreSQL not running. 12 of 21 tests cannot execute. All errors are `ConnectionDoesNotExistError` — no code failures detected.

---

## Summary

**9/9 unit tests PASS** — file parser (7), MoodleClient config (2).

**12 integration/E2E tests cannot run** — PostgreSQL not available. All code is structurally present and wired: models, repos, services, routers, schemas, migrations, file parser, MoodleClient. No test failures, only setup errors due to missing DB.

**4 spec gaps** identified (email encryption test, audit trail tests, tenant isolation test, Moodle WS HTTP tests). These are test gaps, not necessarily implementation gaps — the code may work but lacks verification.

**Recommendation**: Start PostgreSQL (`docker compose up -d db`), re-run, then address the 4 gaps.
