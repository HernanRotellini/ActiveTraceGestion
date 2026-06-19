import api from '@/shared/services/api'
import type {
  SlotEncuentroResponse,
  SlotEncuentroPayload,
  InstanciaEncuentroResponse,
  InstanciaEncuentroPayload,
  InstanciaEncuentroUpdate,
  EncuentrosFilters,
  AdminInstanciasFilters,
} from '@/features/encuentros/types'

const BASE = '/api/v1/encuentros'

export async function listarSlots(filters?: EncuentrosFilters) {
  const { data } = await api.get<SlotEncuentroResponse[]>(`${BASE}/slots`, { params: filters })
  return data
}

export async function crearSlot(payload: SlotEncuentroPayload) {
  const { data } = await api.post<SlotEncuentroResponse>(`${BASE}/slots`, payload)
  return data
}

export async function listarInstancias(filters?: EncuentrosFilters) {
  const { data } = await api.get<InstanciaEncuentroResponse[]>(`${BASE}/instancias`, { params: filters })
  return data
}

export async function crearInstancia(payload: InstanciaEncuentroPayload) {
  const { data } = await api.post<InstanciaEncuentroResponse>(`${BASE}/instancias`, payload)
  return data
}

export async function actualizarInstancia(id: string, update: InstanciaEncuentroUpdate) {
  const { data } = await api.patch<InstanciaEncuentroResponse>(`${BASE}/instancias/${id}`, update)
  return data
}

export async function generarHtml(instanciaId: string) {
  const { data } = await api.get<{ html: string }>(`${BASE}/instancias/${instanciaId}/html`)
  return data
}

export async function adminListarInstancias(filters?: AdminInstanciasFilters) {
  const { data } = await api.get<InstanciaEncuentroResponse[]>(`${BASE}/admin/instancias`, { params: filters })
  return data
}
