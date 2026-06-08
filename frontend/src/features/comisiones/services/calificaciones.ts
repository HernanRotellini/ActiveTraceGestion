import api from '@/shared/services/api'
import type {
  Calificacion,
  ActividadDetectada,
  UmbralConfig,
  AtrasadosResponse,
  RankingItem,
  NotasFinalesItem,
} from '@/features/comisiones/types/calificaciones'

export async function importarCalificaciones(
  comisionId: string,
  file: File,
): Promise<{ actividades: ActividadDetectada[] }> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(`/calificaciones/${comisionId}/importar`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function confirmarImportacion(
  comisionId: string,
  actividadIds: string[],
): Promise<{ count: number }> {
  const response = await api.post(`/calificaciones/${comisionId}/confirmar`, { actividad_ids: actividadIds })
  return response.data
}

export async function listarCalificaciones(
  comisionId: string,
  params?: { materia?: string; alumno?: string },
): Promise<Calificacion[]> {
  const response = await api.get(`/calificaciones/${comisionId}`, { params })
  return response.data
}

export async function configurarUmbral(
  comisionId: string,
  data: Partial<UmbralConfig>,
): Promise<UmbralConfig> {
  const response = await api.put(`/calificaciones/${comisionId}/umbral`, data)
  return response.data
}

export async function obtenerUmbral(comisionId: string): Promise<UmbralConfig> {
  const response = await api.get(`/calificaciones/${comisionId}/umbral`)
  return response.data
}

export async function obtenerAtrasados(comisionId: string): Promise<AtrasadosResponse> {
  const response = await api.get(`/calificaciones/${comisionId}/atrasados`)
  return response.data
}

export async function obtenerRanking(comisionId: string): Promise<RankingItem[]> {
  const response = await api.get(`/calificaciones/${comisionId}/ranking`)
  return response.data
}

export async function obtenerNotasFinales(comisionId: string): Promise<NotasFinalesItem[]> {
  const response = await api.get(`/calificaciones/${comisionId}/notas-finales`)
  return response.data
}
