import api from '@/shared/services/api'
import type {
  CompletionReportResponse,
  EntregasPendientesResponse,
} from '@/features/entregas-sin-corregir/types/entregas'

export async function detectarEntregas(
  comision?: string,
): Promise<EntregasPendientesResponse> {
  const params = comision ? { comision } : undefined
  const response = await api.get<EntregasPendientesResponse>('/entregas/pendientes', { params })
  return response.data
}

export async function exportarEntregas(comision?: string): Promise<Blob> {
  const params = comision ? { comision } : undefined
  const response = await api.get('/entregas/pendientes/exportar', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function importarReporteLms(
  materiaId: string,
  cohorteId: string,
  file: File,
): Promise<CompletionReportResponse> {
  const formData = new FormData()
  formData.append('archivo', file)
  const response = await api.post<CompletionReportResponse>(
    '/calificaciones/completion-report',
    formData,
    {
      params: { materia_id: materiaId, cohorte_id: cohorteId },
      headers: { 'Content-Type': 'multipart/form-data' },
    },
  )
  return response.data
}
