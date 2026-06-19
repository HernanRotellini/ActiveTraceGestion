import api from '@/shared/services/api'
import type { AvisoResponse, AvisoListResponse, AvisoPayload, AvisosFilters, AvisoStatsResponse } from '@/features/avisos/types'

export async function listarAvisos(filters?: AvisosFilters) {
  const { data } = await api.get<AvisoResponse[]>('/api/admin/avisos', { params: filters })
  return data
}

export async function obtenerAviso(id: string) {
  const { data } = await api.get<AvisoResponse>(`/api/admin/avisos/${id}`)
  return data
}

export async function crearAviso(payload: AvisoPayload) {
  const { data } = await api.post<AvisoResponse>('/api/admin/avisos', payload)
  return data
}

export async function actualizarAviso(id: string, payload: Partial<AvisoPayload>) {
  const { data } = await api.put<AvisoResponse>(`/api/admin/avisos/${id}`, payload)
  return data
}

export async function desactivarAviso(id: string) {
  await api.delete(`/api/admin/avisos/${id}`)
}

export async function obtenerStatsAviso(id: string) {
  const { data } = await api.get<AvisoStatsResponse>(`/api/admin/avisos/${id}/stats`)
  return data
}

export async function listarAvisosVisibles(materia_id?: string, cohorte_id?: string) {
  const { data } = await api.get<AvisoListResponse[]>('/api/avisos', { params: { materia_id, cohorte_id } })
  return data
}

export async function confirmarLectura(avisoId: string) {
  await api.post(`/api/avisos/${avisoId}/ack`)
}
