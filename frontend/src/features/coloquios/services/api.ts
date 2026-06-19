import api from '@/shared/services/api'
import type {
  EvaluacionCreate,
  EvaluacionListResponse,
  EvaluacionResponse,
  ReservaResponse,
  ResultadoCreate,
  ResultadoResponse,
  MetricasColoquiosResponse,
  AgendaReservaResponse,
  ColoquiosFilters,
} from '@/features/coloquios/types'

const BASE = '/coloquios'

export async function panelMetricas() {
  const { data } = await api.get<MetricasColoquiosResponse>(`${BASE}/metricas`)
  return data
}

export async function listarConvocatorias(filters?: ColoquiosFilters) {
  const { data } = await api.get<EvaluacionListResponse[]>(BASE, { params: filters })
  return data
}

export async function obtenerConvocatoria(id: string) {
  const { data } = await api.get<EvaluacionResponse>(`${BASE}/${id}`)
  return data
}

export async function crearConvocatoria(payload: EvaluacionCreate) {
  const { data } = await api.post<EvaluacionResponse>(BASE, payload)
  return data
}

export async function cerrarConvocatoria(id: string) {
  const { data } = await api.delete<{ mensaje: string }>(`${BASE}/${id}`)
  return data
}

export async function importarAlumnos(id: string, alumno_ids: string[]) {
  const { data } = await api.post<{ importados: number }>(`${BASE}/${id}/importar-alumnos`, { alumno_ids })
  return data
}

export async function listarTurnos(id: string) {
  const { data } = await api.get<ReservaResponse[]>(`${BASE}/${id}/turnos`)
  return data
}

export async function listarReservas(id: string) {
  const { data } = await api.get<ReservaResponse[]>(`${BASE}/${id}/reservas`)
  return data
}

export async function registrarResultado(id: string, payload: ResultadoCreate) {
  const { data } = await api.post<ResultadoResponse>(`${BASE}/${id}/resultados`, payload)
  return data
}

export async function listarResultados(id: string) {
  const { data } = await api.get<ResultadoResponse[]>(`${BASE}/${id}/resultados`)
  return data
}

export async function agendaGlobal() {
  const { data } = await api.get<{ items: AgendaReservaResponse[]; total: number }>(`${BASE}/admin/agenda`)
  return data
}
