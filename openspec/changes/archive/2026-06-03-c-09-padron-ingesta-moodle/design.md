## Context

Actualmente el sistema tiene los modelos de estructura académica (Carrera, Cohorte, Materia) y de usuarios/asignaciones (Usuario, Asignacion). No existe un mecanismo para registrar qué alumnos pertenecen a cada materia×cohorte. Los módulos posteriores (calificaciones C-10, atrasados C-11, comunicaciones C-12) necesitan esta base.

El padrón debe soportar dos orígenes:
1. **Importación manual** desde archivo `.xlsx`/`.csv` — flujo con preview antes de confirmar.
2. **Sincronización automática** vía Moodle Web Services — sync nocturna + on-demand, con fallback manual si el Moodle no expone WS.

Existe una tensión conocida entre RN-05 ("upsert destructivo, no se conserva historial") y el modelo E6 versionado. Este diseño adopta el modelo versionado de la KB: cada carga crea una nueva versión; al activar una, la anterior se desactiva pero se conserva.

## Goals / Non-Goals

**Goals:**
- Modelo versionado `VersionPadron` + `EntradaPadron` con una versión activa por `(materia_id, cohorte_id)`.
- Endpoint `POST /api/padron/importar` con subida de archivo, preview, y confirmación.
- Endpoint `POST /api/moodle/sync` para sync on-demand + scheduler para sync nocturna.
- Endpoint `DELETE /api/padron/materia/{materia_id}/vaciar` con scope `(usuario_id, materia_id)`.
- Auditoría `PADRON_CARGAR` en cada importación/sync.
- La entrada de padrón puede existir sin `usuario_id` (alumno sin cuenta en el sistema).
- Tests de versionado, import xlsx/csv, mock Moodle WS con fallback 502, aislamiento tenant.

**Non-Goals:**
- No se implementa la importación de calificaciones (eso es C-10).
- No se implementan los flujos de preview desde Moodle WS (solo desde archivo).
- No se implementa la gestión de "grupos" de Moodle más allá de la comisión.
- No se implementa UI frontend (solo API).

## Decisions

### D1 — Versionado explícito con activación manual
**Decisión**: `VersionPadron` tiene un flag `activa: bool`. Al crear una nueva versión sobre `(materia_id, cohorte_id)`, se desactiva la versión activa anterior y se activa la nueva en una misma transacción.
**Alternativa considerada**: upsert destructivo (RN-05 original). Se descarta porque elimina trazabilidad y el modelo E6 explícitamente pide versionado.
**Consecuencia**: las consultas de "alumnos activos de una materia" siempre filtran por `version_padron.activa = true`.

### D2 — Preview como paso previo a la confirmación
**Decisión**: El import tiene dos pasos:
1. `POST /api/padron/preview`: sube el archivo, lo parsea, devuelve `{columnas_detectadas, filas_parseadas (primeras N), total_filas}`.
2. `POST /api/padron/confirmar`: confirma la importación recibiendo un token de preview. Crea la nueva versión y las entradas.
**Alternativa considerada**: import en un solo paso. Se descarta porque F1.3/F1.4 requieren preview.
**Consecuencia**: se necesita almacenamiento temporal del preview (en memoria o caché con TTL corto).

### D3 — Cliente Moodle WS como integration aislada
**Decisión**: El cliente Moodle WS vive en `integrations/moodle_ws.py` como clase `MoodleClient` con métodos `sync_usuarios(materia_id)`, `sync_actividades(materia_id)`. Usa httpx async.
**Alternativa considerada**: meter la lógica en el servicio de padron. Se descarta porque la integración es un módulo independiente con su propio lifecycle y testing.
**Consecuencia**: el servicio `PadronService` inyecta `MoodleClient` como dependencia opcional. Si no está configurado (sin credenciales), opera solo con import manual.

### D4 — Vaciado con scope `(usuario_id, materia_id)`
**Decisión**: `DELETE /api/padron/materia/{materia_id}/vaciar` elimina lógicamente (soft delete) las versiones de padrón creadas por el usuario autenticado para esa materia. No afecta versiones de otros usuarios.
**Alternativa considerada**: eliminar físicamente. Se descarta por la regla de soft delete transversal.
**Consecuencia**: la operación es reversible (restore) y queda auditada.

### D5 — Cifrado de email en EntradaPadron
**Decisión**: El campo `email` de `EntradaPadron` se almacena cifrado (AES-256), igual que en `Usuario`. El resto de campos (nombre, apellidos, comision, regional) van en texto plano.
**Consecuencia**: reusa el helper de cifrado de `app/core/encryption.py` creado en C-02.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| Archivos xlsx/csv malformados causan 500 | Parser con validación estricta + errores descriptivos por fila |
| Preview token expira antes de confirmar | TTL de 30 minutos, suficiente para revisión humana |
| Sync Moodle WS falla por red | Reintento con backoff (3 intentos), fallback a import manual |
| VersionPadron sin `usuario_id` (alumno sin cuenta) | Se registra igual con nombre/apellido/email; se vincula cuando el usuario se crea vía un job de matching |
| Muchas versiones de padrón (decenas) | Solo la activa importa para consultas; listar versiones está paginado |
