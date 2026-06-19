import api from '@/shared/services/api'
import type { MonitorFilters, MonitorResponse } from '@/features/monitores/types/monitores'

export async function obtenerMonitor(filters?: MonitorFilters): Promise<MonitorResponse> {
  const response = await api.get('/api/analisis/monitor', { params: filters })
  return response.data
}
