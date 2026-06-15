import api from '@/shared/services/api'
import type { PeriodoAcademico, PeriodoPayload, FechaPayload, ProgramaPayload } from '@/features/setup-cuatrimestre/types'

export async function listarPeriodos() {
  console.log('[PeriodosAPI] GET /periodos-academicos')
  const { data } = await api.get<{ items: PeriodoAcademico[] }>('/periodos-academicos')
  console.log('[PeriodosAPI] GET /periodos-academicos response →', data)
  return data
}

export async function obtenerPeriodo(id: string) {
  console.log(`[PeriodosAPI] GET /periodos-academicos/${id}`)
  const { data } = await api.get<PeriodoAcademico>(`/periodos-academicos/${id}`)
  console.log(`[PeriodosAPI] GET /periodos-academicos/${id} response →`, data)
  return data
}

export async function crearPeriodo(payload: PeriodoPayload) {
  console.log('[PeriodosAPI] POST /periodos-academicos payload →', payload)
  const { data } = await api.post<PeriodoAcademico>('/periodos-academicos', payload)
  console.log('[PeriodosAPI] POST /periodos-academicos response →', data)
  return data
}

export async function actualizarPeriodo(id: string, payload: Partial<PeriodoPayload>) {
  console.log(`[PeriodosAPI] PATCH /periodos-academicos/${id} payload →`, payload)
  const { data } = await api.patch<PeriodoAcademico>(`/periodos-academicos/${id}`, payload)
  console.log(`[PeriodosAPI] PATCH /periodos-academicos/${id} response →`, data)
  return data
}

export async function activarPeriodo(id: string) {
  console.log(`[PeriodosAPI] POST /periodos-academicos/${id}/activar`)
  const { data } = await api.post<PeriodoAcademico>(`/periodos-academicos/${id}/activar`)
  console.log(`[PeriodosAPI] POST /periodos-academicos/${id}/activar response →`, data)
  return data
}

export async function desactivarPeriodo(id: string) {
  console.log(`[PeriodosAPI] POST /periodos-academicos/${id}/desactivar`)
  const { data } = await api.post<PeriodoAcademico>(`/periodos-academicos/${id}/desactivar`)
  console.log(`[PeriodosAPI] POST /periodos-academicos/${id}/desactivar response →`, data)
  return data
}

export async function agregarFecha(periodoId: string, payload: FechaPayload) {
  console.log(`[PeriodosAPI] POST /periodos-academicos/${periodoId}/fechas payload →`, payload)
  const { data } = await api.post(`/periodos-academicos/${periodoId}/fechas`, payload)
  console.log(`[PeriodosAPI] POST /periodos-academicos/${periodoId}/fechas response →`, data)
  return data
}

export async function quitarFecha(periodoId: string, fechaId: string) {
  console.log(`[PeriodosAPI] DELETE /periodos-academicos/${periodoId}/fechas/${fechaId}`)
  await api.delete(`/periodos-academicos/${periodoId}/fechas/${fechaId}`)
  console.log(`[PeriodosAPI] DELETE /periodos-academicos/${periodoId}/fechas/${fechaId} OK`)
}

export async function agregarPrograma(periodoId: string, payload: ProgramaPayload) {
  console.log(`[PeriodosAPI] POST /periodos-academicos/${periodoId}/programas payload →`, payload)
  const { data } = await api.post(`/periodos-academicos/${periodoId}/programas`, payload)
  console.log(`[PeriodosAPI] POST /periodos-academicos/${periodoId}/programas response →`, data)
  return data
}

export async function quitarPrograma(periodoId: string, programaId: string) {
  console.log(`[PeriodosAPI] DELETE /periodos-academicos/${periodoId}/programas/${programaId}`)
  await api.delete(`/periodos-academicos/${periodoId}/programas/${programaId}`)
  console.log(`[PeriodosAPI] DELETE /periodos-academicos/${periodoId}/programas/${programaId} OK`)
}
