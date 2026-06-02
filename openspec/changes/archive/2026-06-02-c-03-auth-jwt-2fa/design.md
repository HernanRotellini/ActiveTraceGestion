## Context

`c-03-auth-jwt-2fa` construye el cimiento de identidad después de `c-02-core-models-y-tenancy`. El sistema ya cuenta con Tenant, mixins, repository tenant-scoped, soft delete, cifrado en reposo y migración inicial; ahora debe poder autenticar usuarios y emitir sesiones verificables para que C-04 pueda resolver RBAC sobre una identidad confiable.

El dominio es CRÍTICO: cualquier fuga de identidad, token reutilizable indebidamente, password insegura o tenant derivado desde request rompe las reglas duras del proyecto. La autenticación propia está cerrada por ADR-001 para MVP: email + password, 2FA TOTP opcional, JWT access 15 minutos y refresh token con rotación.

## Goals / Non-Goals

**Goals:**
- Implementar usuarios/credenciales mínimos tenant-scoped para login propio.
- Hashear passwords con Argon2id y nunca almacenar ni loguear passwords en texto plano.
- Emitir access JWT firmados de vida corta con claims mínimos y sin permisos.
- Implementar refresh tokens opacos con rotación, revocación y detección de reuso.
- Implementar 2FA TOTP opcional por usuario antes de emitir sesión completa.
- Implementar recuperación de contraseña con token de un solo uso, expiración corta e invalidación tras uso.
- Implementar rate limiting de login 5/60s por IP+email.
- Exponer dependency de usuario actual que resuelve identidad y tenant exclusivamente desde JWT verificado.

**Non-Goals:**
- Resolver permisos finos, guards `require_permission(...)` o matriz RBAC; pertenece a C-04.
- Implementar impersonación; pertenece a audit/RBAC posteriores.
- Implementar frontend de login o formularios; pertenece a C-21.
- Integrar Moodle SSO; queda fuera del MVP de este change.
- Enviar emails reales de recuperación; este change puede dejar puerto/servicio interno mockeable sin violar DB tests.

## Decisions

1. **Access JWT corto + refresh opaco persistido.**
   - Decisión: access token JWT firmado expira en 15 minutos; refresh token es opaco, se almacena hasheado y se rota en cada uso.
   - Alternativa: refresh JWT autocontenido. Se descarta porque la revocación/reuso serían más difíciles de controlar server-side.
   - Rationale: minimiza impacto de robo de access token y permite cortar sesiones con estado persistido.

2. **Claims mínimos y sin permisos en JWT.**
   - Decisión: incluir `sub`/`user_id`, `tenant_id`, `roles`, `exp` y metadatos mínimos necesarios; nunca permisos efectivos.
   - Alternativa: incluir permisos en el token. Se descarta porque C-04 debe resolver permisos server-side por vigencia y tenant.
   - Rationale: mantiene el token liviano y evita permisos stale.

3. **Identidad derivada solo de token verificado.**
   - Decisión: `get_current_user` ignora cualquier `user_id`, `tenant_id` o `roles` proveniente de URL/body/header y valida solo claims firmados + existencia de usuario activo.
   - Alternativa: aceptar `tenant_id` request-scoped para facilitar pruebas. Se descarta por regla de oro.
   - Rationale: previene escalación horizontal/cross-tenant.

4. **2FA como estado intermedio de login.**
   - Decisión: credenciales correctas con TOTP habilitado devuelven un challenge temporal de corta vida; no se emiten access/refresh hasta verificar TOTP.
   - Alternativa: emitir sesión parcial con permisos limitados. Se descarta por complejidad y riesgo.
   - Rationale: fail-closed y flujo simple de testear.

5. **Rate limiting local por IP+email para MVP.**
   - Decisión: implementar componente in-memory/testeable para 5 intentos/60s, con interfaz reemplazable por Redis si escala.
   - Alternativa: persistir intentos en DB desde el inicio. Se descarta por complejidad operacional para MVP.
   - Rationale: cubre el requisito y mantiene bajo acoplamiento.

6. **Tokens sensibles almacenados hasheados.**
   - Decisión: refresh tokens y recovery tokens se devuelven una sola vez, y en DB se guarda hash + expiración + revocación/uso.
   - Alternativa: almacenar tokens en claro. Se descarta por seguridad.
   - Rationale: una fuga de DB no permite usar tokens activos directamente.

7. **Resolución anónima de tenant por `tenant_code` solo en login.**
   - Decisión: `POST /api/auth/login` recibe `tenant_code` para resolver el tenant server-side antes de buscar credenciales; después de emitir sesión, tenant e identidad salen exclusivamente del JWT verificado.
   - Alternativa: login sin contexto de tenant o tenant por header. Se descarta porque el email es único por tenant y un header sería otro canal implícito de identidad.
   - Rationale: permite credential lookup tenant-scoped sin violar la regla de sesión para requests autenticadas.

## Risks / Trade-offs

- **Riesgo: aún no existe el modelo Usuario completo de C-07.** → Mitigación: crear un `AuthUser`/`User` mínimo compatible con tenant, UUID y soft delete, dejando PII/assignments para C-07.
- **Riesgo: rate limiter in-memory no sirve en múltiples réplicas.** → Mitigación: encapsular interfaz para reemplazo por Redis; documentar como MVP local.
- **Riesgo: recovery sin email real no valida entrega end-to-end.** → Mitigación: testear generación/uso/expiración; integración de correo queda para worker/comunicaciones.
- **Riesgo: claims de roles antes de RBAC podrían quedar simples.** → Mitigación: roles son claim mínimo de sesión; permisos no se guardan en token y C-04 podrá reemplazar/expandir resolución server-side.

## Migration Plan

1. Agregar migración Alembic posterior a tenant foundation para tablas mínimas de auth: usuarios/credenciales, refresh sessions, 2FA secrets/challenges y recovery tokens.
2. Usar `tenant_id` en tablas de auth tenant-scoped y aplicar soft delete donde corresponda.
3. Probar upgrade/rollback en PostgreSQL real de test.
4. No migrar datos existentes porque todavía no hay usuarios de producción.

## Open Questions

- Ninguna bloqueante para C-03. La matriz final de roles/permisos se resolverá en C-04; este change solo transporta roles mínimos en claims sin autorizar acciones por permisos.
