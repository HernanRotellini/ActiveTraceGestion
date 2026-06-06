## Context

C-12 implementa el módulo de comunicaciones de activia-trace: cola asíncrona de mensajes a alumnos con preview obligatorio, envío masivo, aprobación humana configurable y worker de despacho. Depende de C-11 (analisis-atrasados-reportes) para obtener la lista de alumnos atrasados a quienes enviar.

Este módulo es el primero que introduce un worker asíncrono en el sistema. El stack es Python 3.13 + FastAPI async + SQLAlchemy 2.0 async + PostgreSQL.

## Goals / Non-Goals

**Goals:**
- Modelo `Comunicacion` con máquina de estados, cifrado AES-256 en destinatario, soft delete, agrupación por lote
- Preview de mensajes con sustitución de variables `{{nombre}}`, `{{materia}}`, `{{comision}}`
- Envío masivo que encola un mensaje por alumno atrasado
- Worker asíncrono que procesa Pendiente → Enviando → Enviado/Error
- Aprobación humana configurable por tenant (flag en tenant settings)
- API REST completa con 7 endpoints
- Permisos `comunicacion:enviar` y `comunicacion:aprobar`
- Audit actions `COMUNICACION_ENVIAR`, `COMUNICACION_APROBAR`, `COMUNICACION_CANCELAR`
- Strict TDD: cobertura ≥90% reglas de negocio

**Non-Goals:**
- Integración real SMTP/API de email (stub/simulación; el delivery real es un change futuro)
- Plantillas persistentes (las plantillas se pasan en cada request)
- Mensajería interna (F3.4, es otro change)
- Bandeja de mensajes (F3.4)
- Tablón de avisos (F3.5)

## Decisions

### D1 — Worker sin framework de colas externo
**Elección**: el worker se implementa como un bucle asyncio que consulta la DB periódicamente (polling cada N segundos), sin Redis/Celery/ARQ.
**Razón**: el volumen esperado es bajo (decenas a cientos de mensajes por día, no millones). Introducir Redis/Celery agrega complejidad operativa innecesaria en esta etapa. El ADR-003 (worker de mails) está pendiente de resolución; usamos la solución más simple que funciona. Migrar a una cola externa más adelante es straight-forward porque la lógica de negocio está encapsulada en el service.
**Alternativa considerada**: Celery — descartada por sobrecarga de dependencias. ARQ (Redis) — descartada por la misma razón.

### D2 — Variables de sustitución por string.replace simple
**Elección**: las variables `{{nombre}}`, `{{materia}}`, `{{comision}}` se reemplazan con `str.replace()` en el service, sin motor de templates.
**Razón**: el set de variables es pequeño (3 fijas), no hay lógica condicional ni loops en las plantillas. Jinja2 agregaría una dependencia sin beneficio real.
**Alternativa considerada**: Jinja2 — descartada por sobreingeniería para el caso de uso.

### D3 — Flag de aprobación obligatoria en Tenant settings (JSONB)
**Elección**: el flag `aprobacion_comunicaciones_obligatoria` se almacena en un campo JSONB `settings` del modelo Tenant (o en una tabla `TenantSettings` existente), no como columna separada.
**Razón**: es una config booleana más del tenant; no justifica una columna dedicada. El patrón JSONB ya existe en el sistema para configuraciones. Si el modelo Tenant no tiene campo `settings`, se agrega una migración para crearlo.
**Alternativa considerada**: Columna dedicada `aprobacion_obligatoria` — descartada porque cada nueva config requeriría migración, violando el patrón JSONB del sistema.

### D4 — Stub de envío en worker
**Elección**: el "envío real" es una función `simular_envio(destinatario, asunto, cuerpo)` que simula latencia (0.5s) y retorna éxito 95% del tiempo / error 5%.
**Razón**: necesitamos probar toda la cadena (cola, estados, reintentos) sin depender de un gateway de email real. Cuando llegue el delivery real, solo se reemplaza esta función.
**Implementación**: `backend/workers/stubs.py`

### D5 — Polling worker con sleep configurable
**Elección**: el worker itera cada `COMUNICACIONES_POLL_INTERVAL` segundos (default: 30), consulta comunicaciones Pendiente que puedan procesarse y las despacha en lotes.
**Razón**: simplicidad. Si en el futuro se necesita menor latencia, se migra a un modelo de notificación (pub/sub o cola).
**Implementación**: `backend/workers/comunicaciones_worker.py`

## Modelo de datos

```python
# backend/models/comunicacion.py
class Comunicacion(Base):
    __tablename__ = "comunicaciones"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("tenants.id"), nullable=False)
    enviado_por_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("usuarios.id"), nullable=False)
    materia_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("materias.id"), nullable=False)
    destinatario: Mapped[str] = mapped_column(Text, nullable=False)  # cifrado AES-256
    asunto: Mapped[str] = mapped_column(String(255), nullable=False)
    cuerpo: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoComunicacion] = mapped_column(
        Enum(EstadoComunicacion), nullable=False, default=EstadoComunicacion.PENDIENTE
    )
    lote_id: Mapped[uuid.UUID] = mapped_column(UUID, nullable=False, index=True)
    enviado_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # soft delete
```

Enumeración de estados (RN-15):
```python
class EstadoComunicacion(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ENVIANDO = "Enviando"
    ENVIADO = "Enviado"
    ERROR = "Error"
    CANCELADO = "Cancelado"
```

## Arquitectura del Worker

```
ComunicacionWorker (asyncio loop)
  │
  ├── poll() cada N segundos
  │   ├── query ComunicacionRepository.pendientes_para_procesar(tenant_id)
  │   │   → estado=Pendiente AND (aprobacion no requerida OR lote aprobado)
  │   │
  │   └── for each comunicación:
  │       ├── 1. transicionar a Enviando
  │       ├── 2. descifrar destinatario
  │       ├── 3. simular_envio(destinatario, asunto, cuerpo)
  │       │   ├── éxito → transicionar a Enviado + registrar enviado_at
  │       │   └── fallo → transicionar a Error
  │       └── 4. audit log COMUNICACION_ENVIAR
```

## API Routes

| Método | Path | Guard | Descripción |
|--------|------|-------|-------------|
| POST | `/api/comunicaciones/preview` | `comunicacion:enviar` | Preview con sustitución de variables |
| POST | `/api/comunicaciones/enviar` | `comunicacion:enviar` | Encola comunicaciones por alumno atrasado |
| GET | `/api/comunicaciones/lotes` | `comunicacion:enviar` | Lista lotes con estados agregados |
| GET | `/api/comunicaciones/lotes/{lote_id}` | `comunicacion:enviar` | Detalle de comunicaciones en un lote |
| POST | `/api/comunicaciones/lotes/{lote_id}/aprobar` | `comunicacion:aprobar` | Aprueba lote (Pendiente→Enviando) |
| POST | `/api/comunicaciones/lotes/{lote_id}/cancelar` | `comunicacion:aprobar` | Cancela lote (Pendiente→Cancelado) |
| POST | `/api/comunicaciones/{id}/cancelar` | `comunicacion:aprobar` | Cancela comunicación individual |

## Estructura de archivos

```
backend/
├── models/
│   └── comunicacion.py           # SQLAlchemy model + EstadoComunicacion enum
├── models/enums.py                # (extender con EstadoComunicacion si existe)
├── schemas/
│   └── comunicacion.py           # Pydantic schemas (request/response)
├── repositories/
│   └── comunicacion_repository.py # Queries scope tenant
├── services/
│   └── comunicacion_service.py   # Lógica de negocio: preview, enviar, aprobar, cancelar
├── routers/
│   └── comunicaciones.py         # FastAPI router con guards
├── workers/
│   ├── comunicaciones_worker.py  # Bucle asyncio de polling
│   └── stubs.py                  # Envío simulado
├── tests/
│   ├── test_comunicacion_model.py
│   ├── test_comunicacion_service.py
│   ├── test_comunicacion_api.py
│   └── test_comunicacion_worker.py
└── migrations/
    └── versions/
        └── xxxx_comunicaciones.py  # Nueva migración Alembic
```

## Permisos y auditoría

- `comunicacion:enviar`: seed en tabla `permiso`. Roles: PROFESOR (propio), COORDINADOR, ADMIN
- `comunicacion:aprobar`: seed en tabla `permiso`. Roles: COORDINADOR, ADMIN
- Audit actions: `COMUNICACION_ENVIAR`, `COMUNICACION_APROBAR`, `COMUNICACION_CANCELAR`

## Template de variables

Variables soportadas en asunto y cuerpo:
- `{{nombre}}` → nombre del alumno (desde `EntradaPadron`)
- `{{materia}}` → nombre de la materia
- `{{comision}}` → comisión del alumno (desde `EntradaPadron`)

## Configuration

Variables de entorno / settings:
- `COMUNICACIONES_POLL_INTERVAL`: segundos entre polls del worker (default: 30)
- `COMUNICACIONES_STUB_SUCCESS_RATE`: probabilidad de éxito del stub (default: 0.95)

Flag por tenant (JSONB en Tenant.settings):
- `aprobacion_comunicaciones_obligatoria`: bool (default: false)

## Risks / Trade-offs

- **[Worker polling vs event-driven]** Polling cada 30s introduce latencia de hasta 30s en el despacho. Aceptable para el volumen esperado. → Mitigación: hacer el intervalo configurable.
- **[Stub de envío]** No hay validación real de entregabilidad. → Mitigación: el stub es fácil de reemplazar; la integración real se especifica en cambio futuro.
- **[Aprobación por lote vs individual]** La aprobación/cancelación individual tiene sentido operativo pero agrega complejidad a la UI. → Mitigación: la API lo soporta; el frontend decide cuándo exponerlo.
- **[Sin reintentos automáticos]** Un mensaje en Error queda en Error. No hay reintento automático. → Mitigación: el usuario puede re-enviar manualmente desde la UI (crea nueva comunicación).
