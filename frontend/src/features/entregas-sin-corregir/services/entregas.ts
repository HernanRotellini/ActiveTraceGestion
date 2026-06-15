import api from '@/shared/services/api'
import type { EntregaPendiente } from '@/features/entregas-sin-corregir/types/entregas'

export async function detectarEntregas(
  comisionId?: string,
): Promise<EntregaPendiente[]> {
  const params = comisionId ? { comision_id: comisionId } : undefined
  console.log('[EntregasAPI] GET /entregas/pendientes params →', params)
  const response = await api.get<{ items: EntregaPendiente[]; total: number }>('/entregas/pendientes', { params })
  console.log('[EntregasAPI] GET /entregas/pendientes response →', response.data)
  return response.data.items
}

export async function exportarEntregas(comisionId?: string): Promise<Blob> {
  const params = comisionId ? { comision_id: comisionId } : undefined
  console.log('[EntregasAPI] GET /entregas/pendientes/exportar params →', params)
  const response = await api.get('/entregas/pendientes/exportar', {
    params,
    responseType: 'blob',
  })
  console.log('[EntregasAPI] GET /entregas/pendientes/exportar → Blob recibido')
  return response.data
}
