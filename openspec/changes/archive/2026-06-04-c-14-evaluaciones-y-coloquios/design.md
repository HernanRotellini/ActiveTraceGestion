## Context

C-14 implementa el módulo de coloquios (Épica 7) sobre la base de C-07 (usuarios-y-asignaciones). El sistema necesita soportar convocatorias de evaluación oral donde COORDINADOR/ADMIN definen fechas con cupos, importan alumnos habilitados, y los ALUMNOS reservan turnos. El modelo de datos está definido en KB §E14 (Evaluacion, ReservaEvaluacion, ResultadoEvaluacion), pero se refina para incluir `TurnoEvaluacion` como entidad separada que representa día+cupo dentro de una convocatoria.

## Goals / Non-Goals

**Goals:**
- Modelo completo: `Evaluacion` (convocatoria), `TurnoEvaluacion` (día/cupo), `ReservaEvaluacion` (reserva alumno), `ResultadoEvaluacion` (nota final)
- CRUD de convocatorias con días y cupos configurables (F7.3)
- Importación de alumnos desde padrón a una convocatoria (F7.2)
- Listado de convocatorias con métricas: total convocados, reservas activas, cupos libres (F7.4)
- Panel de métricas global: instancias activas, alumnos cargados, reservas, notas registradas (F7.1)
- Admin global: registro consolidado de resultados, agenda de reservas (F7.5)
- Reserva de turno por ALUMNO: selecciona día con cupo, bloquea el cupo, permite cancelación
- Permisos: `coloquios:gestionar` (COORDINADOR/ADMIN), `coloquios:reservar` (ALUMNO)
- Tenant isolation en toda operación
- Auditoría de acciones significativas (creación, importación, reserva, cancelación, registro de nota)

**Non-Goals:**
- Integración con Moodle para publicación automática de fechas
- Notificaciones automáticas al alumno al reservar/cancelar (se hará vía módulo de comunicaciones)
- Cola de aprobación de reservas (la reserva es directa si hay cupo)
- Límite de reservas por alumno (1 activa por convocatoria, pero sin tope histórico)
- UI de frontend (queda para C-21 o posterior)

## Decisions

### D1 — `TurnoEvaluacion` como entidad separada vs. JSONB en Evaluacion

**Decisión**: Modelar `TurnoEvaluacion` como tabla independiente.

- **Alternativa**: Almacenar días/cupos como JSONB en `Evaluacion.dias_disponibles`.
- **Razón**: Los turnos necesitan operaciones atómicas de decremento de cupo, consulta individual, y son referenciados por `ReservaEvaluacion`. Con JSONB, cada reserva requeriría leer y reescribir todo el campo, con riesgo de race conditions. Una tabla dedicada permite UPDATE atómico del cupo (`cupo_restante = cupo_restante - 1 WHERE cupo_restante > 0`).

### D2 — Reserva con cupo protegido por UPDATE atómico

**Decisión**: La reserva decrementa `cupo_restante` en `TurnoEvaluacion` dentro de la misma transacción que crea `ReservaEvaluacion`, usando `UPDATE ... SET cupo_restante = cupo_restante - 1 WHERE cupo_restante > 0`.

- **Alternativa**: Leer cupo, decidir en Python, luego insertar.
- **Razón**: La alternativa tiene race condition entre la lectura y la escritura. El UPDATE condicional en SQL es atómico y previene sobre-reserva.

### D3 — Importación de alumnos como tabla puente `ConvocatoriaAlumno`

**Decisión**: Crear tabla `ConvocatoriaAlumno` (evaluacion_id, usuario_id, creado_at) para registrar qué alumnos están habilitados en una convocatoria.

- **Alternativa**: Usar `EntradaPadron` directamente filtrando por materia/cohorte.
- **Razón**: No todos los alumnos del padrón están habilitados para coloquio (solo los que regularizan la materia). La tabla puente permite importación selectiva.

### D4 — API bajo `/api/coloquios` con guards de permiso

**Decisión**: Un solo router `coloquios.py` con prefijo `/api/coloquios`. Los endpoints de gestión usan guard `coloquios:gestionar`; los de reserva usan `coloquios:reservar`; los de consulta de métricas usan `coloquios:gestionar`.

- **Endpoints**:
  - `GET /api/coloquios/metricas` — panel de métricas global (F7.1)
  - `POST /api/coloquios` — crear convocatoria (F7.3)
  - `GET /api/coloquios` — listar convocatorias (F7.4)
  - `GET /api/coloquios/{id}` — detalle de convocatoria
  - `POST /api/coloquios/{id}/importar-alumnos` — importar alumnos (F7.2)
  - `POST /api/coloquios/{id}/turnos` — agregar/quitar turnos
  - `GET /api/coloquios/{id}/turnos` — listar turnos con disponibilidad
  - `POST /api/coloquios/{id}/reservar` — alumno reserva turno
  - `POST /api/coloquios/{id}/cancelar-reserva` — alumno cancela reserva
  - `GET /api/coloquios/{id}/reservas` — listar reservas (gestión)
  - `POST /api/coloquios/{id}/resultados` — registrar resultados (admin)
  - `GET /api/coloquios/{id}/resultados` — consultar resultados consolidados
  - `DELETE /api/coloquios/{id}` — cerrar/eliminar convocatoria

### D5 — Sin cifrado AES (no hay PII)

**Decisión**: Los modelos de coloquios no manejan datos personales. Solo referencian `usuario_id` (UUID) y `materia_id` (UUID). No se requiere cifrado en reposo.

### D6 — Estados de ReservaEvaluacion

- `Activa`: turno reservado, cupo descontado
- `Cancelada`: alumno canceló, cupo se restituye

Al cancelar, se incrementa `cupo_restante` en el `TurnoEvaluacion` correspondiente.

## Modelo de datos

```sql
Evaluacion {
  id              UUID        — PK
  tenant_id       UUID        — FK → tenants
  materia_id      UUID        — FK → materias
  cohorte_id      UUID        — FK → cohortes
  tipo            enum        — Parcial | TP | Coloquio | Recuperatorio
  instancia       text        — "Coloquio Final", "Recuperatorio 1"
  estado          enum        — Activa | Cerrada
  created_at      timestamptz
  updated_at      timestamptz
  deleted_at      timestamptz
}

TurnoEvaluacion {
  id              UUID        — PK
  tenant_id       UUID        — FK → tenants
  evaluacion_id   UUID        — FK → evaluaciones
  fecha           date        — día del turno
  hora_inicio     time        — opcional
  hora_fin        time        — opcional
  cupo_maximo     int         — cupo total definido
  cupo_restante   int         — cupo disponible (decrementado al reservar)
  created_at      timestamptz
  updated_at      timestamptz
  deleted_at      timestamptz
}

ReservaEvaluacion {
  id              UUID        — PK
  tenant_id       UUID        — FK → tenants
  evaluacion_id   UUID        — FK → evaluaciones
  turno_id        UUID        — FK → turnos_evaluacion
  alumno_id       UUID        — FK → usuarios (ALUMNO)
  estado          enum        — Activa | Cancelada
  created_at      timestamptz
  updated_at      timestamptz
  deleted_at      timestamptz
}

ResultadoEvaluacion {
  id              UUID        — PK
  tenant_id       UUID        — FK → tenants
  evaluacion_id   UUID        — FK → evaluaciones
  alumno_id       UUID        — FK → usuarios
  nota_final      text        — numérica o cualitativa
  registrado_por  UUID        — FK → usuarios (quien registró)
  created_at      timestamptz
  updated_at      timestamptz
  deleted_at      timestamptz
}

ConvocatoriaAlumno {
  id              UUID        — PK
  tenant_id       UUID        — FK → tenants
  evaluacion_id   UUID        — FK → evaluaciones
  alumno_id       UUID        — FK → usuarios (ALUMNO)
  created_at      timestamptz
}
```

## Risks / Trade-offs

- **[Race condition en reserva]** → Mitigado por UPDATE atómico con WHERE condicional (D2). La transacción encapsula UPDATE + INSERT.
- **[Sobre-reserva por reintento]** → Mitigado: si el UPDATE afecta 0 filas (sin cupo), la transacción falla y el servicio retorna error. El alumno ve "sin cupo disponible".
- **[Cancelación restituye cupo]** → Riesgo: si se cancela una reserva antigua y otro alumno reserva inmediatamente después, se puede exceder el cupo original. Mitigado: el cupo_restante se maneja como contador exacto; cancelar siempre incrementa, reservar siempre decrementa. El saldo converge.
- **[Rendimiento en métricas]** → Las métricas globales (F7.1) consultan agregaciones sobre 4 tablas. Con decenas de convocatorias, es liviano. Con cientos, considerar cache o tabla de métricas denormalizadas.
- **[Dependencia de C-07]** → Sin C-07 no existen usuarios ni asignaciones. Este módulo depende de que C-07 esté completado (confirmado en CHANGES.md).
