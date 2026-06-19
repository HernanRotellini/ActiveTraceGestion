import api from '@/shared/services/api'
import type { TareaPayload, TareaEstado, ComentarioPayload, TareasFilters, TareaResponse, TareaDetailResponse, ComentarioResponse } from '@/features/tareas-internas/types'

export async function listarTareas(filters?: TareasFilters) {
  const { data } = await api.get<TareaResponse[]>('/tareas', { params: filters })
  return data
}

export async function listarMisTareas(limit = 100, offset = 0) {
  const { data } = await api.get<TareaResponse[]>('/tareas/mis', { params: { limit, offset } })
  return data
}

export async function obtenerTarea(id: string) {
  const { data } = await api.get<TareaDetailResponse>(`/tareas/${id}`)
  return data
}

export async function crearTarea(payload: TareaPayload) {
  const { data } = await api.post<TareaResponse>('/tareas', payload)
  return data
}

export async function cambiarEstadoTarea(id: string, estado: TareaEstado) {
  const { data } = await api.patch<TareaResponse>(`/tareas/${id}/estado`, { estado })
  return data
}

export async function delegarTarea(id: string, asignado_a: string) {
  const { data } = await api.post<TareaResponse>(`/tareas/${id}/delegar`, { asignado_a })
  return data
}

export async function crearComentario(tareaId: string, payload: ComentarioPayload) {
  const { data } = await api.post<ComentarioResponse>(`/tareas/${tareaId}/comentarios`, payload)
  return data
}
