import api from '@/shared/services/api'
import type { EntregaPendiente } from '@/features/entregas-sin-corregir/types/entregas'

export async function detectarEntregas(
  comision?: string,
): Promise<EntregaPendiente[]> {
  const params = comision ? { comision } : undefined
  const response = await api.get<{ items: EntregaPendiente[]; total: number }>('/entregas/pendientes', { params })
  return response.data.items
}

export async function exportarEntregas(comision?: string): Promise<Blob> {
  const params = comision ? { comision } : undefined
  const response = await api.get('/entregas/pendientes/exportar', {
    params,
    responseType: 'blob',
  })
  return response.data
}
