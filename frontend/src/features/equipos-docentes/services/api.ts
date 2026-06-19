import api from '@/shared/services/api'
import type {
  AsignacionListFilters,
  AsignacionEquipoResponse,
  CrearAsignacionesEquipoPayload,
  ClonePayload,
  VigenciaPayload,
  ExportarEquiposParams,
} from '@/features/equipos-docentes/types'

export async function listarAsignaciones(filters?: AsignacionListFilters) {
  const { data } = await api.get<AsignacionEquipoResponse[]>('/asignaciones', { params: filters })
  return data
}

export async function crearAsignacionesEquipo(payload: CrearAsignacionesEquipoPayload) {
  const { data } = await api.post<AsignacionEquipoResponse[]>('/equipos/asignacion-masiva', payload)
  return data
}

export async function clonarEquipo(payload: ClonePayload) {
  const { data } = await api.post('/equipos/clonar', payload)
  return data
}

export async function actualizarVigencia(payload: VigenciaPayload) {
  const { data } = await api.patch('/equipos/vigencia', payload)
  return data
}

export async function exportarEquiposCSV(params: ExportarEquiposParams) {
  const { data } = await api.get('/equipos/exportar', { params, responseType: 'blob' })
  return data as Blob
}
