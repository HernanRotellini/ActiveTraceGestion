import api from '@/shared/services/api'
import type { Aviso, AvisoPayload, AvisosFilters } from '@/features/avisos/types'

export async function listarAvisos(filters?: AvisosFilters) {
  const { data } = await api.get<Aviso[] | { items: Aviso[]; total: number }>(
    '/admin/avisos',
    { params: filters },
  )

  if (Array.isArray(data)) {
    return { items: data, total: data.length }
  }

  return {
    items: data.items ?? [],
    total: data.total ?? data.items?.length ?? 0,
  }
}

export async function obtenerAviso(id: string) {
  const { data } = await api.get<Aviso>(`/admin/avisos/${id}`)
  return data
}

export async function crearAviso(payload: AvisoPayload) {
  const { data } = await api.post<Aviso>('/admin/avisos', payload)
  return data
}

export async function actualizarAviso(id: string, payload: Partial<AvisoPayload>) {
  const { data } = await api.put<Aviso>(`/admin/avisos/${id}`, payload)
  return data
}

export async function publicarAviso(id: string) {
  const { data } = await api.put<Aviso>(`/admin/avisos/${id}`, { activo: true })
  return data
}

export async function archivarAviso(id: string) {
  const { data } = await api.delete(`/admin/avisos/${id}`)
  return data
}
