## 1. Backend — Nuevos permisos en constantes y seed

- [x] 1.1 Agregar las 9 constantes de permisos nuevos a `backend/app/models/permisos.py`
- [x] 1.2 Crear migración Alembic que agrega los 9 permisos a la tabla `permisos`
- [x] 1.3 En la misma migración, asignar permisos a roles según matriz: ver `design.md` D1
- [x] 1.4 Agregar `liquidaciones:operar_grilla`, `liquidaciones:calcular_cerrar`, `facturas:gestionar` al rol ADMIN
- [x] 1.5 Ejecutar migración y verificar que los permisos existen en DB

## 2. Backend — Separar guards GET vs POST/PUT/DELETE

- [x] 2.1 `calificaciones.py`: `GET /api/calificaciones` usa `calificaciones:ver`
- [x] 2.2 `avisos.py`: GETs usan `avisos:ver`, POST/PUT/DELETE usan `avisos:gestionar`
- [x] 2.3 `equipos.py`: GET usa `equipos:ver`, POST/PATCH usan `equipos:gestionar`
- [x] 2.4 `encuentros.py`: GETs usan `encuentros:ver`, POST/PATCH usan `encuentros:gestionar`
- [x] 2.5 `coloquios.py`: GETs usan `coloquios:ver`, POST/DELETE usan `coloquios:gestionar`
- [x] 2.6 `tareas.py`: GETs usan `tareas:ver`, POST/PATCH usan `tareas:gestionar`
- [x] 2.7 `liquidaciones.py`: GETs usan `liquidaciones:ver`, POST preview/cerrar usan `liquidaciones:gestionar`
- [x] 2.8 `facturas.py`: GETs usan `liquidaciones:ver`, POST/PUT/DELETE usan `facturas:gestionar`

## 3. Backend — /api/auth/me devuelve permisos y nombre

- [x] 3.1 Agregar campo `permissions: list[str]` al schema `CurrentUserResponse`
- [x] 3.2 Agregar campos `nombre: str` y `apellidos: str` al schema `CurrentUserResponse`
- [x] 3.3 Modificar endpoint `/auth/me` para calcular `effective_permissions()` y consultar `nombre`/`apellidos` del usuario
- [x] 3.4 Probar que el endpoint devuelve permisos correctos para cada rol

## 4. Frontend — Propagar permisos desde /auth/me

- [x] 4.1 Agregar `permissions: string[]` al tipo `MeResponse` en `auth/types.ts`
- [x] 4.2 Agregar `nombre: string | null` y `apellidos: string | null` al tipo `MeResponse`
- [x] 4.3 Modificar `useLogin.ts` para pasar `permissions: me.permissions`, `nombre`, `apellidos` al `setSession()`
- [x] 4.4 Modificar `useChallenge2fa.ts` igual
- [x] 4.5 Verificar que `session.user.permissions` tenga datos para no-ADMIN

## 5. Frontend — Mostrar nombre legible en footer

- [x] 5.1 Agregar `nombre`, `apellidos` al tipo `SessionUser` en `session.ts`
- [x] 5.2 Modificar `MainLayout.tsx` para mostrar `"{nombre} {apellidos} — {rol}"` en el footer inferior izquierdo
- [x] 5.3 Si no hay nombre, mostrar email como fallback

## 6. Frontend — Actualizar PermissionGuard en rutas

- [x] 6.1 Verificar que todos los `requiredPermissions` en `routes/index.tsx` coinciden con los nombres canónicos del backend
- [x] 6.2 Los nombres ya son correctos (coinciden con lo que se agregó al backend)

## 7. Verificación — Backend por rol

- [x] 7.1 Verificar permisos de ADMIN (debe tener todos)
- [x] 7.2 Verificar permisos de COORDINADOR (debe tener todos los listados — nota: `estructura:gestionar` no está asignado a COORDINADOR, ver diseño §Riesgos)
- [x] 7.3 Verificar permisos de PROFESOR (debe tener: calificaciones:ver, atrasados:ver, comunicacion:enviar, tareas:gestionar, encuentros:gestionar, avisos:confirmar)
- [x] 7.4 Verificar permisos de TUTOR (debe tener: atrasados:ver, encuentros:gestionar, guardias:registrar, avisos:confirmar)
- [x] 7.5 Verificar permisos de FINANZAS (debe tener: liquidaciones:ver, liquidaciones:operar_grilla, liquidaciones:gestionar, facturas:gestionar, auditoria:ver, avisos:confirmar)
- [x] 7.6 Verificar permisos de NEXO (solo debe tener: avisos:confirmar)

## 8. Verificación — Frontend end-to-end

- [x] 8.1 Login como ADMIN: ver todas las pantallas, sin 403 (bypass en `hasPermission`)
- [x] 8.2 Login como COORDINADOR: sidebar filtra correctamente según permisos
- [x] 8.3 Login como PROFESOR: sidebar filtra correctamente según permisos
- [x] 8.4 Login como FINANZAS: sidebar filtra correctamente según permisos
- [x] 8.5 Login como NEXO: solo pantalla de inicio (sidebar limitado)
- [x] 8.6 El footer muestra nombre legible vs UUID (verificado en código)
