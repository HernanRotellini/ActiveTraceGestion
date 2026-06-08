import api from '@/shared/services/api'
import type { Encuentro, EncuentroPayload, EncuentrosFilters } from '@/features/encuentros/types'

export async function listarEncuentros(filters?: EncuentrosFilters) {
  const { data } = await api.get<{ items: Encuentro[]; total: number }>('/encuentros', { params: filters })
  return data
}

export async function obtenerEncuentro(id: string) {
  const { data } = await api.get<Encuentro>(`/encuentros/${id}`)
  return data
}

export async function crearEncuentro(payload: EncuentroPayload) {
  const { data } = await api.post<Encuentro>('/encuentros', payload)
  return data
}

export async function actualizarEncuentro(id: string, payload: Partial<EncuentroPayload>) {
  const { data } = await api.patch<Encuentro>(`/encuentros/${id}`, payload)
  return data
}

export async function eliminarEncuentro(id: string) {
  await api.delete(`/encuentros/${id}`)
}

export async function agregarGuardia(encuentroId: string, payload: { docente_id: string; hora_inicio: string; hora_fin: string }) {
  const { data } = await api.post(`/encuentros/${encuentroId}/guardias`, payload)
  return data
}

export async function quitarGuardia(encuentroId: string, guardiaId: string) {
  await api.delete(`/encuentros/${encuentroId}/guardias/${guardiaId}`)
}
