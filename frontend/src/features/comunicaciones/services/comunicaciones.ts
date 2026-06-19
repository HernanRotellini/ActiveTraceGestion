import api from '@/shared/services/api'
import type {
  AccionResponse,
  EnvioMasivoRequest,
  EnvioMasivoResponse,
  LoteDetalleResponse,
  LotesListResponse,
  MateriaOption,
  PreviewRequest,
  PreviewResponse,
} from '@/features/comunicaciones/types/comunicaciones'

export async function fetchMaterias(): Promise<MateriaOption[]> {
  const { data } = await api.get<{ items: MateriaOption[]; total: number }>('/admin/materias')
  return data.items
}

export async function generarPreview(data: PreviewRequest): Promise<PreviewResponse> {
  const response = await api.post<PreviewResponse>('/comunicaciones/preview', data)
  return response.data
}

export async function enviarMasivo(data: EnvioMasivoRequest): Promise<EnvioMasivoResponse> {
  const response = await api.post<EnvioMasivoResponse>('/comunicaciones/enviar', data)
  return response.data
}

export async function listarLotes(): Promise<LotesListResponse> {
  const response = await api.get<LotesListResponse>('/comunicaciones/lotes')
  return response.data
}

export async function detalleLote(loteId: string): Promise<LoteDetalleResponse> {
  const response = await api.get<LoteDetalleResponse>(`/comunicaciones/lotes/${loteId}`)
  return response.data
}

export async function aprobarLote(loteId: string): Promise<AccionResponse> {
  const response = await api.post<AccionResponse>(`/comunicaciones/lotes/${loteId}/aprobar`)
  return response.data
}

export async function cancelarLote(loteId: string): Promise<AccionResponse> {
  const response = await api.post<AccionResponse>(`/comunicaciones/lotes/${loteId}/cancelar`)
  return response.data
}

export async function cancelarComunicacion(comunicacionId: string): Promise<AccionResponse> {
  const response = await api.post<AccionResponse>(`/comunicaciones/${comunicacionId}/cancelar`)
  return response.data
}
