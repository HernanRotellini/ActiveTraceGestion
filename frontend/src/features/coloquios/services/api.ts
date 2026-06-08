import api from '@/shared/services/api'
import type { EvaluacionColoquio, ColoquioPayload, ColoquiosFilters, ResultadoColoquio } from '@/features/coloquios/types'

export async function listarColoquios(filters?: ColoquiosFilters) {
  const { data } = await api.get<{ items: EvaluacionColoquio[]; total: number }>('/coloquios', { params: filters })
  return data
}

export async function obtenerColoquio(id: string) {
  const { data } = await api.get<EvaluacionColoquio>(`/coloquios/${id}`)
  return data
}

export async function crearColoquio(payload: ColoquioPayload) {
  const { data } = await api.post<EvaluacionColoquio>('/coloquios', payload)
  return data
}

export async function actualizarColoquio(id: string, payload: Partial<ColoquioPayload>) {
  const { data } = await api.patch<EvaluacionColoquio>(`/coloquios/${id}`, payload)
  return data
}

export async function confirmarReserva(coloquioId: string, reservaId: string) {
  const { data } = await api.post(`/coloquios/${coloquioId}/reservas/${reservaId}/confirmar`)
  return data
}

export async function cancelarReserva(coloquioId: string, reservaId: string) {
  const { data } = await api.post(`/coloquios/${coloquioId}/reservas/${reservaId}/cancelar`)
  return data
}

export async function registrarResultado(coloquioId: string, reservaId: string, resultado: ResultadoColoquio, nota?: number) {
  const { data } = await api.post(`/coloquios/${coloquioId}/reservas/${reservaId}/resultado`, { resultado, nota })
  return data
}
