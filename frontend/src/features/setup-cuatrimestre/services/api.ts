import api from '@/shared/services/api'
import type {
  FechaAcademicaOficial,
  FechaAcademicaOficialPayload,
  FechaAcademicaOficialUpdatePayload,
  PeriodoAcademico,
  PeriodoPayload,
  FechaPayload,
  ProgramaPayload,
  ProgramaOficial,
  ProgramaOficialPayload,
  ProgramaOficialUpdatePayload,
  TipoFechaAcademica,
} from '@/features/setup-cuatrimestre/types'

export async function listarPeriodos() {
  const { data } = await api.get<{ items: PeriodoAcademico[] }>('/periodos-academicos')
  return data
}

export async function obtenerPeriodo(id: string) {
  const { data } = await api.get<PeriodoAcademico>(`/periodos-academicos/${id}`)
  return data
}

export async function crearPeriodo(payload: PeriodoPayload) {
  const { data } = await api.post<PeriodoAcademico>('/periodos-academicos', payload)
  return data
}

export async function actualizarPeriodo(id: string, payload: Partial<PeriodoPayload>) {
  const { data } = await api.patch<PeriodoAcademico>(`/periodos-academicos/${id}`, payload)
  return data
}

export async function activarPeriodo(id: string) {
  const { data } = await api.post<PeriodoAcademico>(`/periodos-academicos/${id}/activar`)
  return data
}

export async function desactivarPeriodo(id: string) {
  const { data } = await api.post<PeriodoAcademico>(`/periodos-academicos/${id}/desactivar`)
  return data
}

export async function eliminarPeriodo(id: string) {
  await api.delete(`/periodos-academicos/${id}`)
}

export async function agregarFecha(periodoId: string, payload: FechaPayload) {
  const { data } = await api.post(`/periodos-academicos/${periodoId}/fechas`, payload)
  return data
}

export async function quitarFecha(periodoId: string, fechaId: string) {
  await api.delete(`/periodos-academicos/${periodoId}/fechas/${fechaId}`)
}

export async function agregarPrograma(periodoId: string, payload: ProgramaPayload) {
  const { data } = await api.post(`/periodos-academicos/${periodoId}/programas`, payload)
  return data
}

export async function quitarPrograma(periodoId: string, programaId: string) {
  await api.delete(`/periodos-academicos/${periodoId}/programas/${programaId}`)
}

export interface ProgramasFilters {
  materia_id?: string
  carrera_id?: string
  cohorte_id?: string
}

export interface FechasFilters {
  periodo_id?: string
  materia_id?: string
  cohorte_id?: string
  tipo?: TipoFechaAcademica
  periodo?: string
}

export async function listarProgramas(filters?: ProgramasFilters) {
  const { data } = await api.get<ProgramaOficial[]>('/programas', { params: filters })
  return data
}

export async function crearPrograma(payload: ProgramaOficialPayload) {
  const { data } = await api.post<ProgramaOficial>('/programas', payload)
  return data
}

export async function actualizarPrograma(id: string, payload: ProgramaOficialUpdatePayload) {
  const { data } = await api.put<ProgramaOficial>(`/programas/${id}`, payload)
  return data
}

export async function eliminarPrograma(id: string) {
  await api.delete(`/programas/${id}`)
}

export async function listarFechas(filters?: FechasFilters) {
  const { data } = await api.get<FechaAcademicaOficial[]>('/fechas-academicas', { params: filters })
  return data
}

export async function crearFecha(payload: FechaAcademicaOficialPayload) {
  const { data } = await api.post<FechaAcademicaOficial>('/fechas-academicas', payload)
  return data
}

export async function actualizarFecha(id: string, payload: FechaAcademicaOficialUpdatePayload) {
  const { data } = await api.put<FechaAcademicaOficial>(`/fechas-academicas/${id}`, payload)
  return data
}

export async function eliminarFecha(id: string) {
  await api.delete(`/fechas-academicas/${id}`)
}
