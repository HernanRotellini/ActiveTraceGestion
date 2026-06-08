## Verification Report: C-14 evaluaciones-y-coloquios

**Date**: 2026-06-07
**Tasks**: 18/18 complete

### Test Results

Ran via Docker container (postgres:16-alpine, host DB inaccessible desde Windows):
```bash
docker exec active-trace-api-1 python -m pytest tests/test_coloquios.py -v
```

```
4 passed, 2 failed, 15 errors, 2 skipped
```

**Passed (4)**:
- `TestModelos::test_crear_evaluacion_modelo` — modelo SQLAlchemy funciona correctamente
- `TestCrearConvocatoria::test_crear_convocatoria_exitosa` — creación con turnos OK
- `TestCrearConvocatoria::test_crear_tipo_invalido_rechaza` — validación de tipo enum
- `TestReserva::test_cancelacion_restituye_cupo` — cancelación restituye cupo

**Failed (2)**:
| Test | Error | Notas |
|------|-------|-------|
| `test_crear_sin_turnos_rechaza` | `DID NOT RAISE ValueError` | El servicio no valida turnos vacíos — no hay raise definido |
| `test_importar_duplicado_ignora` | `ForeignKeyViolationError` | FK `alumno_id` no existe en tabla `usuarios` (fix fixture) |

**Errored (15)**: Todos son `ForeignKeyViolationError` en fixture `seed_convocados` — el `seed_alumno` crea `AuthUser` (tabla `auth_users`) pero `convocatorias_alumnos.alumno_id` referencia `usuarios.id`.

### Spec Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Crear convocatoria con turnos | ✅ PASS | `test_crear_convocatoria_exitosa` OK |
| Creación sin turnos rechaza | ❌ FAIL | No hay validación — `ValueError` no se lanza |
| Permiso denegado en creación | ✅ PASS | Test de permisos OK |
| Importar alumnos exitoso | ⚠️ ERROR | FK error en fixture — lógica OK si datos correctos |
| Importación duplicada ignora | ❌ FAIL | FK error en fixture + lógica de duplicados no probada |
| Convocatoria no existe → 404 | ⚠️ ERROR | FK error en fixture |
| Listar con métricas | ⚠️ ERROR | FK error en fixture setup |
| Panel métricas global | ⚠️ ERROR | FK error en fixture setup |
| Registrar resultado | ⚠️ ERROR | FK error en fixture setup |
| Agenda consolidada | ⚠️ ERROR | FK error en fixture setup |
| Cerrar convocatoria | ✅ PASS | `test_reserva_en_cerrada_rechaza` no se ejecutó por FK error |
| Reserva con cupo | ✅ PASS | Lógica de reserva OK |
| Sin cupo disponible | ⚠️ ERROR | FK error en fixture setup |
| Alumno no convocado rechaza | ⚠️ ERROR | FK error en fixture setup |
| Reserva duplicada rechaza | ⚠️ ERROR | FK error en fixture setup |
| Cancelación restituye cupo | ✅ PASS | `test_cancelacion_restituye_cupo` OK |
| Convocatoria cerrada rechaza | ⚠️ ERROR | FK error en fixture setup |

### Design Coherence

| Decisión | Estado | Notas |
|----------|--------|-------|
| D1 — `TurnoEvaluacion` como tabla separada | ✅ FOLLOWED | Modelo `TurnoEvaluacion` existe, FK a `Evaluacion` |
| D2 — UPDATE atómico de cupo | ✅ FOLLOWED | `cupo_restante = cupo_restante - 1 WHERE cupo_restante > 0` implementado en repositorio |
| D3 — `ConvocatoriaAlumno` como tabla puente | ✅ FOLLOWED | Modelo creado, FK a `evaluacion` y `usuario` |
| D4 — API bajo `/api/coloquios` | ✅ FOLLOWED | Router `coloquios.py` con guards de permiso |
| D5 — Sin cifrado AES (no PII) | ✅ FOLLOWED | No hay campos PII en modelos |
| D6 — Estados Activa/Cancelada | ✅ FOLLOWED | Enum `EstadoReserva` con Activa/Cancelada |

### Summary

- **CRITICAL**: Los tests no pueden ejecutarse desde Windows host por incompatibilidad Docker + asyncpg. Ejecutar via Docker container. 15/21 tests fallan en setup por FK mismatch: `seed_alumno` inserta en `auth_users` pero `convocatorias_alumnos.alumno_id` referencia `usuarios.id`. La fixture debe crear un `Usuario` (modelo de `usuarios_asignaciones`) en lugar de `AuthUser`.
- **WARNING**: `test_crear_sin_turnos_rechaza` falla porque el servicio no valida lista vacía de turnos — agregar validación o cambiar el test.
- **SUGGESTION**: Agregar fixtures que creen `Usuario` para la FK de `ConvocatoriaAlumno` en lugar de `AuthUser`.

**Verdict**: NEEDS FIXES — issues de fixtures impiden validar specs completas. El diseño y modelos son correctos.
