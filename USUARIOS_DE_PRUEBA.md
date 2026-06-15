# Usuarios de Prueba — activia-trace

> Credenciales para testing del sistema.
> **Tenant:** `UTN_MENDOZA_GLOBAL`
> **Password (todos):** `test123`

| Rol | Nombre | Email | Pantallas disponibles |
|-----|--------|-------|----------------------|
| **PROFESOR** | Carlos Gutiérrez | `profesor@test.com` | Mis Comisiones, Entregas, Comunicaciones (scope propio), Monitor |
| **PROFESOR** (facturante) | Fernando García | `profesor2@test.com` | Mis Comisiones, Entregas, Comunicaciones, Monitor |
| **PROFESOR** | Sofía Torres | `profesor3@test.com` | Mis Comisiones, Entregas, Comunicaciones, Monitor |
| **TUTOR** | María López | `tutor@test.com` | Mis Comisiones, Entregas, Monitor |
| **TUTOR** | Ana Díaz | `tutor2@test.com` | Mis Comisiones, Entregas, Monitor |
| **COORDINADOR** | Martín Rodríguez | `coordinador@test.com` | Todo Docente + Coordinación + Estructura académica |
| **NEXO** | Laura Fernández | `nexo@test.com` | Avisos, Comunicaciones |
| **ADMIN** | Roberto Pérez | `admin@test.com` | Todas las pantallas |
| **FINANZAS** | Gabriela Martínez | `finanzas@test.com` | Liquidaciones, Grilla salarial, Facturas |

## Datos de prueba creados

### Carreras
- **Licenciatura en Sistemas** (código: `LIC-SIST`)
- **Contador Público** (código: `CONT-PUB`)

### Cohortes activas
- Sistemas 2026, Contador 2026, Sistemas 2025

### Materias — Sistemas
| Código | Nombre | Comisiones |
|--------|--------|-----------|
| `PROG-I` | Programación I | A, B |
| `BD-I` | Base de Datos I | A, B |
| `REDES` | Redes y Comunicaciones | A |
| `ING-SW` | Ingeniería de Software | A, B |

### Materias — Contador
| Código | Nombre | Comisiones |
|--------|--------|-----------|
| `CONT-I` | Contabilidad I | A |
| `IMP-2026` | Impuestos | A |
| `AUDIT` | Auditoría | A |

### Profesores asignados
- **Carlos Gutiérrez** y **Fernando García** → todas las materias de Sistemas (comisiones A, B)
- **Carlos Gutiérrez** y **Sofía Torres** → todas las materias de Contador (comisión A)
- **Sofía Torres** → Redes (comisión A)

### Tutores asignados
- **María López** → todas las materias de Sistemas (comisiones A, B)
- **Ana Díaz** → todas las materias de Contador (comisión A)

### Alumnos en padrón
10 alumnos cargados en todas las materias, repartidos en comisiones A/B, con calificaciones de ejemplo (Parcial 1 y TP Integrador).

### Liquidaciones
- Período actual abiertas para profesores de Sistemas y Contador
- Período anterior (cerrada) para Carlos Gutiérrez

---

## Cómo cargar los datos

```bash
# Asegurate de que las migraciones estén aplicadas
docker compose run --rm api alembic upgrade head

# Ejecutar el seed
docker compose run --rm api python scripts/seed_dev_data.py
```
