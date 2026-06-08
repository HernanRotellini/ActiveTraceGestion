## ADDED Requirements

### Requirement: Dashboard general de alumnos (F2.7)
El sistema SHALL proveer un dashboard con métricas generales de distribución de alumnos por comisión, materia y estado.

#### Scenario: Dashboard muestra métricas generales
- **WHEN** un usuario con `atrasados:ver` navega a `/monitores/general`
- **THEN** se renderizan cards con métricas: total alumnos, alumnos por comisión, distribución por estado

#### Scenario: Filtros por materia y período
- **WHEN** el usuario selecciona una materia y un período en los filtros
- **THEN** las métricas se actualizan para reflejar la selección

#### Scenario: Gráfico de distribución
- **WHEN** el dashboard carga
- **THEN** se muestra un gráfico de barras o torta con la distribución de alumnos por comisión

### Requirement: Dashboard de atrasos y entregas (F2.9)
El sistema SHALL proveer un dashboard con métricas de entregas pendientes, atrasos por materia, y tendencias.

#### Scenario: Dashboard muestra métricas de atrasos
- **WHEN** un usuario navega a la sección de atrasos del monitor general
- **THEN** se muestran cards con: entregas sin corregir, atrasos por materia, promedio de días de atraso

#### Scenario: Tabla de atrasos por materia
- **WHEN** el dashboard carga
- **THEN** se renderiza una tabla con materias ordenadas por cantidad de atrasos

#### Scenario: Exportar métricas a CSV
- **WHEN** el usuario hace clic en "Exportar" en cualquiera de los dashboards
- **THEN** se descarga un CSV con las métricas visibles en ese momento
