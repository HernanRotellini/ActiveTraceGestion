# Comandos Útiles — activia-trace

## 🐳 Docker

```bash
# Iniciar todos los servicios
docker compose up -d

# Ver logs de la API
docker compose logs -f api

# Rebuildear la API (tras cambios en requirements, etc.)
docker compose build api

# Reiniciar un servicio
docker compose restart api
```

## 🗄️ Base de Datos

```bash
# Ingresar a psql
docker exec -it active-trace-postgres-1 psql -U trace -d trace

# Consultas rápidas
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM auth_users"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT email, roles FROM auth_users ORDER BY email"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT codigo, nombre FROM roles WHERE tenant_id = '00000000-0000-0000-0000-000000000001'"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM permisos WHERE tenant_id = '00000000-0000-0000-0000-000000000001'"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM roles_permisos WHERE tenant_id = '00000000-0000-0000-0000-000000000001'"
```

## 🔄 Migraciones (Alembic)

```bash
# Ver el head actual
docker exec active-trace-api-1 alembic current

# Subir todas las migraciones pendientes
docker exec active-trace-api-1 alembic upgrade head

# Hacer stamp del head (si la DB ya tiene las tablas pero alembic no lo sabe)
docker exec active-trace-api-1 alembic stamp head

# Bajar una migración
docker exec active-trace-api-1 alembic downgrade -1
```

## 🌱 Seeds — Orden correcto

Los seeds deben ejecutarse EN ESTE ORDEN después de un reset completo:

### 1. Seed RBAC (roles, permisos, asignaciones)

```bash
docker exec active-trace-api-1 python scripts/seed_rbac.py
```

> Crea 7 roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS), 32 permisos y 85 asignaciones rol→permiso.
> **Idempotente**: se puede ejecutar múltiples veces sin duplicar datos.

### 2. Seed completo de datos de desarrollo

```bash
docker exec active-trace-api-1 python scripts/seed_dev_data.py
```

> Crea: carreras, cohortes, materias, 19 usuarios de prueba, asignaciones docentes, padrón de alumnos, calificaciones, liquidaciones, facturas, tareas internas, avisos, comunicaciones, encuentros, guardias, coloquios, programas académicos, auditoría, mensajería interna.
> **Idempotente**: usa ON CONFLICT DO NOTHING donde es posible.
> **Usuarios creados**: todos con contraseña `test123`, tenant `UTN_MENDOZA_GLOBAL`.

### 3. Verificar que todo esté cargado

```bash
docker exec active-trace-api-1 python scripts/verify_seed.py
```

> Muestra conteo de registros por cada tabla. Si alguna tabla tiene 0 registros, algo falló.

## 👥 Usuarios de Prueba (password: `test123`)

| Email | Rol | Pantallas que puede ver |
|-------|-----|------------------------|
| admin@test.com | ADMIN | Todo |
| coordinador@test.com | COORDINADOR | Gestión académica, equipos, comunicaciones |
| profesor@test.com | PROFESOR | Mis comisiones, calificaciones propias |
| tutor@test.com | TUTOR | Atrasados, encuentros, avisos |
| alumno@test.com | ALUMNO | Estado académico, evaluaciones |
| nexo@test.com | NEXO | Comunicaciones |
| finanzas@test.com | FINANZAS | Liquidaciones, facturas, auditoría |

Para ver todos los usuarios:
```bash
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT email, roles FROM auth_users ORDER BY roles, email"
```

## 🔑 Login (para probar con curl / PowerShell)

```powershell
$body = @{email="admin@test.com"; password="test123"; tenant_code="UTN_MENDOZA_GLOBAL"} | ConvertTo-Json
$login = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -Body $body -ContentType "application/json"
$token = $login.access_token

# Ver permisos del usuario
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Method Get -Headers @{Authorization="Bearer $token"}

# Probar un endpoint protegido
Invoke-RestMethod -Uri "http://localhost:8000/api/admin/materias" -Method Get -Headers @{Authorization="Bearer $token"}
```

## 🔧 Mantenimiento

### Reset completo (destruye todo)

```bash
docker compose down -v
docker compose up -d
# Esperar a que postgres esté listo
docker exec active-trace-api-1 alembic stamp head
docker exec active-trace-api-1 python scripts/seed_rbac.py
docker exec active-trace-api-1 python scripts/seed_dev_data.py
```

### Ver logs de la API en tiempo real

```bash
docker compose logs -f api
```

### Ejecutar un comando Python dentro del container

```bash
docker exec active-trace-api-1 python -c "print('hola')"
```
