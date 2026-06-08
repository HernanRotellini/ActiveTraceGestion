import api from '@/shared/services/api'
import type { MonitorFilters, MonitorAlumno } from '@/features/monitores/types/monitores'

export async function obtenerMonitor(filters?: MonitorFilters): Promise<MonitorAlumno[]> {
  const response = await api.get('/monitor/alumnos', { params: filters })
  return response.data
}

export async function exportarMonitor(filters?: MonitorFilters): Promise<Blob> {
  const response = await api.get('/monitor/alumnos/exportar', {
    params: filters,
    responseType: 'blob',
  })
  return response.data
}
