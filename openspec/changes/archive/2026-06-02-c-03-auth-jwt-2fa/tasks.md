## 1. Safety Net y Modelos de Auth

- [x] 1.1 Ejecutar safety net existente con Docker Python 3.13 + PostgreSQL real antes de modificar backend.
- [x] 1.2 Escribir tests RED para usuario/credenciales auth tenant-scoped: password Argon2id, estado activo/inactivo y migración de tablas auth.
- [x] 1.3 Implementar modelos mínimos de auth, repositories tenant-scoped y migración Alembic de auth.
- [x] 1.4 Triangular tests de migración upgrade/rollback y aislamiento por tenant para usuarios auth.

## 2. Login y Access JWT

- [x] 2.1 Escribir tests RED para login OK, password inválida, usuario inactivo y no emisión de tokens en fallos.
- [x] 2.2 Implementar service/router/schemas de `POST /api/auth/login` con hashing/verificación Argon2id.
- [x] 2.3 Escribir tests RED de claims mínimos JWT: user id, tenant id, roles, exp y ausencia de permisos.
- [x] 2.4 Implementar emisión/verificación de access JWT de 15 minutos con claims mínimos.

## 3. Dependency de Usuario Actual y Logout

- [x] 3.1 Escribir tests RED para `get_current_user`: token válido, token expirado/malformado/firma inválida.
- [x] 3.2 Implementar dependency que resuelve identidad y tenant exclusivamente desde JWT verificado.
- [x] 3.3 Escribir tests RED de identidad inmutable: parámetros/body/header con user_id/tenant_id divergentes no alteran contexto.
- [x] 3.4 Implementar logout que revoca refresh session activa.

## 4. Refresh Token Rotation

- [x] 4.1 Escribir tests RED para refresh válido rota token y preserva user/tenant.
- [x] 4.2 Implementar refresh tokens opacos hasheados, expiración, revocación y endpoint `POST /api/auth/refresh`.
- [x] 4.3 Escribir tests RED para reuso de refresh, refresh expirado y token revocado.
- [x] 4.4 Implementar fail-closed para reuso/expiración/revocación sin emitir tokens nuevos.

## 5. 2FA TOTP

- [x] 5.1 Escribir tests RED para enrolamiento TOTP: secret pendiente y activación solo con código válido.
- [x] 5.2 Implementar enrolamiento/verificación TOTP con secreto cifrado o protegido en reposo.
- [x] 5.3 Escribir tests RED para login con 2FA habilitado: credenciales devuelven challenge, no tokens.
- [x] 5.4 Implementar challenge temporal y emisión de sesión solo tras TOTP válido.
- [x] 5.5 Triangular con TOTP inválido y challenge expirado.

## 6. Recuperación de Contraseña

- [x] 6.1 Escribir tests RED para solicitud de recovery: token de un solo uso para usuario activo y respuesta genérica para email desconocido.
- [x] 6.2 Implementar generación de recovery token hasheado, expiración corta y puerto/servicio de notificación testeable.
- [x] 6.3 Escribir tests RED para reset válido, token usado y token expirado.
- [x] 6.4 Implementar reset de password con invalidación del token y nuevo hash Argon2id.

## 7. Rate Limiting y Verificación Final

- [x] 7.1 Escribir tests RED de rate limit 5 intentos/60s por IP+email, sexto intento bloqueado y reset de ventana.
- [x] 7.2 Implementar rate limiter in-memory con interfaz reemplazable y aplicación antes de validar credenciales.
- [x] 7.3 Ejecutar suite completa del backend con Docker Python 3.13 + PostgreSQL real y registrar evidencia Strict TDD.
- [x] 7.4 Verificar reglas duras: sin permisos en JWT, identidad solo desde sesión, sin mocks de DB, archivos backend ≤500 LOC y flujo Routers → Services → Repositories → Models.
