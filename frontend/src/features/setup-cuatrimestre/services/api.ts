import api from '@/shared/services/api'
import type { PeriodoAcademico, PeriodoPayload, FechaPayload, ProgramaPayload } from '@/features/setup-cuatrimestre/types'

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
