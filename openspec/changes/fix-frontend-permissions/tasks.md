## 1. Backend — Nuevos permisos en constantes y seed

- [ ] 1.1 Agregar las 9 constantes de permisos nuevos a `backend/app/models/permisos.py`
- [ ] 1.2 Crear migración Alembic que agrega los 9 permisos a la tabla `permisos`
- [ ] 1.3 En la misma migración, asignar permisos a roles según matriz: ver `design.md` D1
- [ ] 1.4 Agregar `liquidaciones:operar_grilla`, `liquidaciones:calcular_cerrar`, `facturas:gestionar` al rol ADMIN
- [ ] 1.5 Ejecutar migración y verificar que los permisos existen en DB

## 2. Backend — Separar guards GET vs POST/PUT/DELETE

- [ ] 2.1 `calificaciones.py`: `GET /api/calificaciones` usa `calificaciones:ver`
- [ ] 2.2 `avisos.py`: GETs usan `avisos:ver`, POST/PUT/DELETE usan `avisos:gestionar`
- [ ] 2.3 `equipos.py`: GET usa `equipos:ver`, POST/PATCH usan `equipos:gestionar`
- [ ] 2.4 `encuentros.py`: GETs usan `encuentros:ver`, POST/PATCH usan `encuentros:gestionar`
- [ ] 2.5 `coloquios.py`: GETs usan `coloquios:ver`, POST/DELETE usan `coloquios:gestionar`
- [ ] 2.6 `tareas.py`: GETs usan `tareas:ver`, POST/PATCH usan `tareas:gestionar`
- [ ] 2.7 `liquidaciones.py`: GETs usan `liquidaciones:ver`, POST preview/cerrar usan `liquidaciones:gestionar`
- [ ] 2.8 `facturas.py`: GETs usan `liquidaciones:ver`, POST/PUT/DELETE usan `facturas:gestionar`

## 3. Backend — /api/auth/me devuelve permisos y nombre

- [ ] 3.1 Agregar campo `permissions: list[str]` al schema `CurrentUserResponse`
- [ ] 3.2 Agregar campos `nombre: str` y `apellidos: str` al schema `CurrentUserResponse`
- [ ] 3.3 Modificar endpoint `/auth/me` para calcular `effective_permissions()` y consultar `nombre`/`apellidos` del usuario
- [ ] 3.4 Probar que el endpoint devuelve permisos correctos para cada rol

## 4. Frontend — Propagar permisos desde /auth/me

- [ ] 4.1 Agregar `permissions: string[]` al tipo `MeResponse` en `auth/types.ts`
- [ ] 4.2 Agregar `nombre: string | null` y `apellidos: string | null` al tipo `MeResponse`
- [ ] 4.3 Modificar `useLogin.ts` para pasar `permissions: me.permissions`, `nombre`, `apellidos` al `setSession()`
- [ ] 4.4 Modificar `useChallenge2fa.ts` igual
- [ ] 4.5 Verificar que `session.user.permissions` tenga datos para no-ADMIN

## 5. Frontend — Mostrar nombre legible en footer

- [ ] 5.1 Agregar `nombre`, `apellidos` al tipo `SessionUser` en `session.ts`
- [ ] 5.2 Modificar `MainLayout.tsx` para mostrar `"{nombre} {apellidos} — {rol}"` en el footer inferior izquierdo
- [ ] 5.3 Si no hay nombre, mostrar email como fallback

## 6. Frontend — Actualizar PermissionGuard en rutas

- [ ] 6.1 Verificar que todos los `requiredPermissions` en `routes/index.tsx` coinciden con los nombres canónicos del backend
- [ ] 6.2 Los nombres ya son correctos (coinciden con lo que se agregó al backend)

## 7. Verificación — Backend por rol

- [ ] 7.1 Verificar permisos de ADMIN (debe tener todos)
- [ ] 7.2 Verificar permisos de COORDINADOR (debe tener: avisos:ver, avisos:gestionar, equipos:ver, equipos:gestionar, encuentros:ver, encuentros:gestionar, coloquios:ver, coloquios:gestionar, tareas:ver, tareas:gestionar, atrasados:ver, comunicacion:enviar, comunicacion:aprobar, estructura:gestionar, auditoria:ver, calificaciones:ver, calificaciones:importar)
- [ ] 7.3 Verificar permisos de PROFESOR (debe tener: calificaciones:ver, atrasados:ver, comunicacion:enviar, tareas:gestionar, encuentros:gestionar, avisos:confirmar)
- [ ] 7.4 Verificar permisos de TUTOR (debe tener: atrasados:ver, encuentros:gestionar, guardias:registrar, avisos:confirmar)
- [ ] 7.5 Verificar permisos de FINANZAS (debe tener: liquidaciones:ver, liquidaciones:operar_grilla, liquidaciones:gestionar, facturas:gestionar, auditoria:ver, avisos:confirmar)
- [ ] 7.6 Verificar permisos de NEXO (solo debe tener: avisos:confirmar)

## 8. Verificación — Frontend end-to-end

- [ ] 8.1 Login como ADMIN: ver todas las pantallas, sin 403
- [ ] 8.2 Login como COORDINADOR: ver sidebar filtrado correctamente
- [ ] 8.3 Login como PROFESOR: ver solo comisiones, entregas, comunicaciones, monitor
- [ ] 8.4 Login como FINANZAS: ver solo liquidaciones, facturas, auditoría
- [ ] 8.5 Login como NEXO: ver pantalla de inicio (sin sidebar items)
- [ ] 8.6 Verificar que el footer muestra nombre legible en vez de UUID para cada rol
