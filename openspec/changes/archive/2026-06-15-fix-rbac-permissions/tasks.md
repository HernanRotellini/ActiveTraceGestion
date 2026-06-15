## 1. Crear script de seed RBAC

- [x] 1.1 Crear `backend/scripts/seed_rbac.py` — script idempotente que inserte roles, permisos y asignaciones faltantes para el tenant seed.
- [x] 1.2 Verificar sintaxis del script con `python -c "import py_compile; py_compile.compile(...)"` o ejecución directa.

## 2. Ejecutar seed RBAC

- [x] 2.1 Copiar script al contenedor `active-trace-api-1`.
- [x] 2.2 Ejecutar `docker exec active-trace-api-1 python scripts/seed_rbac.py`.
- [x] 2.3 Verificar que roles, permisos y roles_permisos tengan datos.

## 3. Verificar endpoints

- [x] 3.1 Login como admin@test.com y probar acceso a `/api/admin/materias` (estructura:gestionar).
- [x] 3.2 Login como profesor@test.com y probar acceso a `/api/avisos`, `/api/coloquios` (con nuevo permiso).
- [x] 3.3 Verificar que los 403 anteriores ahora den 200 o el error correcto por falta de datos, no por falta de permiso.
