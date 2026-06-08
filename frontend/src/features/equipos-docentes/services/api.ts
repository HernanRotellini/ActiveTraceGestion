import api from '@/shared/services/api'
import type {
  EquipoDocente,
  AsignacionMasivaPayload,
  ClonePayload,
  VigenciaPayload,
  EquiposFilters,
} from '@/features/equipos-docentes/types'

export async function listarEquipos(filters?: EquiposFilters) {
  const { data } = await api.get<{ items: EquipoDocente[]; total: number }>('/equipos-docentes', { params: filters })
  return data
}

export async function obtenerEquipo(id: string) {
  const { data } = await api.get<EquipoDocente>(`/equipos-docentes/${id}`)
  return data
}

export async function crearEquipo(payload: { materia_id: string; carrera: string }) {
  const { data } = await api.post<EquipoDocente>('/equipos-docentes', payload)
  return data
}

export async function actualizarEquipo(id: string, payload: { materia_id?: string; carrera?: string; estado?: string }) {
  const { data } = await api.patch<EquipoDocente>(`/equipos-docentes/${id}`, payload)
  return data
}

export async function eliminarEquipo(id: string) {
  await api.delete(`/equipos-docentes/${id}`)
}

export async function asignacionMasiva(payload: AsignacionMasivaPayload) {
  const { data } = await api.post('/equipos-docentes/asignacion-masiva', payload)
  return data
}

export async function clonarEquipo(payload: ClonePayload) {
  const { data } = await api.post('/equipos-docentes/clonar', payload)
  return data
}

export async function actualizarVigencia(asignacionId: string, payload: VigenciaPayload) {
  const { data } = await api.patch(`/equipos-docentes/asignaciones/${asignacionId}/vigencia`, payload)
  return data
}

export async function exportarEquiposCSV(filters?: EquiposFilters) {
  const { data } = await api.get('/equipos-docentes/exportar', { params: filters, responseType: 'blob' })
  return data as Blob
}
