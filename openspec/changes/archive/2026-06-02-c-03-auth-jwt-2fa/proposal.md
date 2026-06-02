## Why

Con el cimiento multi-tenant ya archivado, el sistema necesita una autenticación propia y endurecida para emitir sesiones seguras antes de construir RBAC, auditoría o cualquier módulo de negocio. Este change implementa el flujo base de identidad: login con email/password, JWT de vida corta, refresh con rotación, 2FA opcional, recuperación de contraseña y resolución de identidad exclusivamente desde la sesión verificada.

## What Changes

- Introducir modelo(s) mínimos de usuario/sesión necesarios para autenticación: credenciales con password Argon2id, estado activo, roles en claims mínimos y pertenencia a tenant.
- Agregar endpoints anónimos de autenticación: `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `POST /api/auth/forgot`, `POST /api/auth/reset` y endpoints necesarios para enrolar/verificar 2FA TOTP.
- Emitir JWT access token firmado de 15 minutos con claims mínimos (`sub`/`user_id`, `tenant_id`, `roles`, `exp`) y sin permisos.
- Implementar refresh tokens opacos con rotación: cada uso invalida el token anterior y emite un nuevo par; reuso de refresh invalida/falla cerrado.
- Implementar 2FA TOTP opcional por usuario: credenciales válidas no emiten sesión completa hasta superar segundo factor cuando está habilitado.
- Implementar recuperación de contraseña con token de un solo uso, expiración corta e invalidación tras uso.
- Agregar rate limiting de login 5 intentos/60s por IP+email.
- Crear dependency `get_current_user`/sesión actual que resuelve identidad y tenant solo desde JWT verificado; ningún parámetro de request puede alterar actor o tenant.
- Cubrir con Strict TDD: login OK/KO, refresh rotation, reuso de refresh, 2FA, recuperación, rate limit e identidad inmutable por parámetros.

## Capabilities

### New Capabilities
- `user-authentication`: Login/logout, hashing Argon2id, emisión y verificación de JWT access token, dependency de usuario actual e identidad derivada exclusivamente de sesión.
- `refresh-token-rotation`: Gestión de refresh tokens opacos, rotación, revocación, logout y detección de reuso.
- `two-factor-authentication`: Enrolamiento y verificación TOTP opcional por usuario, con gate entre credenciales válidas y emisión de sesión.
- `password-recovery`: Solicitud y confirmación de recuperación de contraseña con tokens de un solo uso y expiración corta.
- `login-rate-limiting`: Límite de intentos de login por IP+email para mitigar fuerza bruta.

### Modified Capabilities
- Ninguna.

## Impact

- Backend: `backend/app/api/v1/routers/`, `backend/app/core/security.py` o módulos de auth equivalentes, `backend/app/core/dependencies.py`, `backend/app/models/`, `backend/app/repositories/`, `backend/app/services/`, `backend/app/schemas/`.
- Base de datos: migración Alembic para usuarios/credenciales, sesiones refresh, secretos 2FA y tokens de recuperación, todas tenant-scoped y soft-deletable donde aplique.
- Seguridad: dominio CRÍTICO; identidad y tenant siempre salen del JWT verificado, no de URL/body/header; fail-closed ante token inválido, refresh reusado o 2FA pendiente.
- Tests: pytest con base PostgreSQL real/efímera, sin mocks de DB; cobertura de reglas de negocio de autenticación y edge cases de seguridad.
