import api from '@/shared/services/api'
import type { Aviso, AvisoPayload, AvisosFilters } from '@/features/avisos/types'

export async function listarAvisos(filters?: AvisosFilters) {
  const { data } = await api.get<{ items: Aviso[]; total: number }>('/avisos', { params: filters })
  return data
}

export async function obtenerAviso(id: string) {
  const { data } = await api.get<Aviso>(`/avisos/${id}`)
  return data
}

export async function crearAviso(payload: AvisoPayload) {
  const { data } = await api.post<Aviso>('/avisos', payload)
  return data
}

export async function actualizarAviso(id: string, payload: Partial<AvisoPayload>) {
  const { data } = await api.patch<Aviso>(`/avisos/${id}`, payload)
  return data
}

export async function publicarAviso(id: string) {
  const { data } = await api.post<Aviso>(`/avisos/${id}/publicar`)
  return data
}

export async function archivarAviso(id: string) {
  const { data } = await api.post<Aviso>(`/avisos/${id}/archivar`)
  return data
}
