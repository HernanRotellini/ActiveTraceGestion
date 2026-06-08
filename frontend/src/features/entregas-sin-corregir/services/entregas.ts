import api from '@/shared/services/api'
import type { EntregaPendiente } from '@/features/entregas-sin-corregir/types/entregas'

export async function detectarEntregas(
  comisionId?: string,
): Promise<EntregaPendiente[]> {
  const response = await api.get('/entregas/pendientes', {
    params: comisionId ? { comision_id: comisionId } : undefined,
  })
  return response.data
}

export async function exportarEntregas(comisionId?: string): Promise<Blob> {
  const response = await api.get('/entregas/pendientes/exportar', {
    params: comisionId ? { comision_id: comisionId } : undefined,
    responseType: 'blob',
  })
  return response.data
}
