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
  const { data } = await api.get<AsignacionEquipoResponse[]>('/api/asignaciones', { params: filters })
  return data
}

export async function crearAsignacionesEquipo(payload: CrearAsignacionesEquipoPayload) {
  const { data } = await api.post<AsignacionEquipoResponse[]>('/api/equipos/asignacion-masiva', payload)
  return data
}

export async function clonarEquipo(payload: ClonePayload) {
  const { data } = await api.post('/api/equipos/clonar', payload)
  return data
}

export async function actualizarVigencia(payload: VigenciaPayload) {
  const { data } = await api.patch('/api/equipos/vigencia', payload)
  return data
}

export async function exportarEquiposCSV(params: ExportarEquiposParams) {
  const { data } = await api.get('/api/equipos/exportar', { params, responseType: 'blob' })
  return data as Blob
}
