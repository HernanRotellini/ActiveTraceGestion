# Checklist — Usuarios

> Fuentes: `knowledge-base/03_actores_y_roles.md`, `backend/app/api/v1/routers/usuarios.py`, `backend/app/schemas/usuarios.py`

## Contratos de API (según backend)

- [x] `POST /api/admin/usuarios` → `UsuarioResponse` (sin password en el payload)
- [x] `GET /api/admin/usuarios` → `UsuarioResponse[]` (sin paginación, filtros: nombre, email)
- [x] `GET /api/admin/usuarios/{id}` → `UsuarioResponse`
- [x] `PATCH /api/admin/usuarios/{id}` → `UsuarioResponse`
- [x] `DELETE /api/admin/usuarios/{id}` → 204 (soft delete)

## Tipos correctos

- [x] `UsuarioAdmin`: id, nombre, apellidos, email, dni?, cuil?, cbu?, alias_cbu?, telefono?, direccion?, estado, legajo?, banco?, facturador, roles? (opcional — no retornado por el backend aún), created_at, updated_at
- [x] `UsuarioAdminPayload`: nombre, apellidos, email, dni?, cuil?, cbu?, alias_cbu?, telefono?, direccion?, legajo?, banco?, facturador?
- [x] `UsuarioAdminFilters`: nombre?, email? (sin page/limit/rol — backend no soporta paginación ni filtro por rol)
- [x] Eliminado `password` de payload y formulario (backend no acepta password en UsuarioCreate)
- [x] Fechas corregidas: `created_at`/`updated_at` (no `creado_en`/`actualizado_en`)
- [x] `roles` ahora es `roles?: string[]` (opcional) ya que el backend no lo retorna en UsuarioResponse

## Servicio

- [x] URL: `/api/admin/usuarios` (con prefix `/api/`)
- [x] `listarUsuarios` retorna `UsuarioAdmin[]` (no `{ items, total }`)

## Hook `useUsuarios`

- [x] Normaliza el array a `{ items: UsuarioAdmin[], total: number }` para no romper todos los callers
- [x] Todos los callers existentes (equipos, tareas, liquidaciones) siguen funcionando con `usuariosResp?.items`

## UsuariosPage

- [x] Filtros: nombre, email (sin page/limit/rol)
- [x] Sin paginación (backend no la soporta)
- [x] Sin campo `password` en formulario
- [x] `roles` en tabla con `u.roles ?? []` (defensivo)
- [x] PII protegida con checkbox "Mostrar PII" y verificación de permiso `usuarios:gestionar`
- [x] Campos PII (DNI, CBU, CUIL, teléfono, dirección, legajo, banco, facturador) solo visibles con permiso

## Criterios transversales

- [x] URL con `/api/` prefix
- [x] Identidad desde JWT (no URL/body)
- [x] RBAC: `usuarios:gestionar` (solo ADMIN)
- [x] Soft delete vía DELETE (implementado en backend)
- [x] PII enmascarada en UI cuando no hay permiso
- [x] Sin `any` en TypeScript
