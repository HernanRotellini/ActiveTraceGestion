import api from '@/shared/services/api'
import type { Tarea, TareaPayload, TareaEstado, ComentarioPayload, TareasFilters } from '@/features/tareas-internas/types'

export async function listarTareas(filters?: TareasFilters) {
  const { data } = await api.get<{ items: Tarea[]; total: number }>('/tareas-internas', { params: filters })
  return data
}

export async function obtenerTarea(id: string) {
  const { data } = await api.get<Tarea>(`/tareas-internas/${id}`)
  return data
}

export async function crearTarea(payload: TareaPayload) {
  const { data } = await api.post<Tarea>('/tareas-internas', payload)
  return data
}

export async function actualizarTarea(id: string, payload: Partial<TareaPayload>) {
  const { data } = await api.patch<Tarea>(`/tareas-internas/${id}`, payload)
  return data
}

export async function cambiarEstadoTarea(id: string, estado: TareaEstado) {
  const { data } = await api.post<Tarea>(`/tareas-internas/${id}/estado`, { estado })
  return data
}

export async function listarComentarios(tareaId: string) {
  const { data } = await api.get<{ items: Tarea['comentarios'] }>(`/tareas-internas/${tareaId}/comentarios`)
  return data
}

export async function crearComentario(tareaId: string, payload: ComentarioPayload) {
  const { data } = await api.post(`/tareas-internas/${tareaId}/comentarios`, payload)
  return data
}
