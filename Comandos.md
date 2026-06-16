# Comandos Útiles — activia-trace

## 🐳 Docker

```bash
# Iniciar todos los servicios
docker compose up -d

# Rebuildear + iniciar la API (tras cambios en código o dependencias)
docker compose up -d --build api

# Ver logs de la API
docker compose logs -f api

# Reiniciar un servicio sin rebuild
docker compose restart api
```

## 🗄️ Base de Datos

```bash
# Ingresar a psql interactivo
docker exec -it active-trace-postgres-1 psql -U trace -d trace

# Consultas rápidas
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM usuarios"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT email, roles FROM auth_users ORDER BY email"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT nombre FROM roles WHERE tenant_id = '00000000-0000-0000-0000-000000000001'"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM permisos"
docker exec active-trace-postgres-1 psql -U trace -d trace -c "SELECT count(*) FROM roles_permisos"
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

Los seeds deben ejecutarse EN ESTE ORDEN después de un reset completo.
Siempre rebuildear la imagen si se agregaron archivos nuevos al backend.

> ⚠️ **IMPORTANTE**: Usar `alembic upgrade head`, NO `stamp head`.
> `stamp` solo marca la revisión sin crear tablas. `upgrade` ejecuta las migraciones.

### 1. Ejecutar migraciones (crea todas las tablas)

```bash
docker exec active-trace-api-1 alembic upgrade head
```

### 2. Seed RBAC (roles, permisos, asignaciones)

```bash
docker exec active-trace-api-1 python scripts/seed_rbac.py
```

> Crea 7 roles, **33 permisos** y **88 asignaciones** rol→permiso.
> **Idempotente**: se puede ejecutar múltiples veces sin duplicar datos.
>
> Permisos incluidos:
> - 23 originales (`atrasados:ver`, `comunicacion:enviar`, `estructura:gestionar`, etc.)
> - 9 de lectura separada (`calificaciones:ver`, `equipos:ver`, `avisos:ver`, etc.)
> - 1 granular (`periodos:gestionar` — para Setup cuatrimestre, asignado a COORDINADOR y ADMIN)

### 3. Seed completo de datos de desarrollo

```bash
docker exec active-trace-api-1 python scripts/seed_dev_data.py
```

> Crea: carreras, cohortes, materias, 19 usuarios de prueba, asignaciones docentes, padrón de alumnos, calificaciones, liquidaciones, facturas, tareas, avisos, comunicaciones, encuentros, guardias, coloquios, programas académicos, auditoría, mensajería interna.
> **Idempotente**: todos con contraseña `test123`, tenant `UTN_MENDOZA_GLOBAL`.

### 4. Verificar que todo esté cargado

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

## 🧪 Tests

> **Nota**: La imagen Docker optimizada excluye las herramientas de test por defecto. Para poder correr las pruebas sobre un contenedor levantado, instala las dependencias de prueba al vuelo ejecutando como `root`.

```bash
# 1. Instalar dependencias de testing al vuelo
docker-compose exec -u root api pip install pytest pytest-asyncio httpx coverage

# 2. Ejecutar todos los tests del backend
docker-compose exec api pytest tests/ -v

# 3. Tests con reporte de cobertura
docker-compose exec api pytest tests/ --cov=app --cov-report=term-missing

# 4. Tests de un módulo específico (ej. cargas del frontend)
docker-compose exec api pytest tests/test_frontend_payloads.py -v
```

## 🔧 Mantenimiento

### Reset completo (destruye todo y reseed)

```bash
# 1. Destruir contenedores + volúmenes
docker compose down -v

# 2. Rebuildear + levantar (esperar a que postgres esté healthy)
docker compose up -d --build api

# 3. Migraciones
docker exec active-trace-api-1 alembic upgrade head

# 4. Seeds (en orden)
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
