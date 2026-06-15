import api from '@/shared/services/api'
import type {
  Liquidacion,
  LiquidacionFilters,
  SalarioBase,
  SalarioBasePayload,
  Plus,
  PlusPayload,
  Factura,
  FacturaPayload,
  FacturaFilters,
} from '@/features/liquidaciones/types'

export async function obtenerLiquidacionActiva(filters?: LiquidacionFilters) {
  const { data } = await api.get<Liquidacion>('/liquidaciones/activa', { params: filters })
  return data
}

export async function obtenerLiquidacion(id: string) {
  const { data } = await api.get<Liquidacion>(`/liquidaciones/${id}`)
  return data
}

export async function cerrarLiquidacion(id: string) {
  const { data } = await api.post<Liquidacion>(`/liquidaciones/${id}/cerrar`)
  return data
}

export async function listarHistorial(filters?: LiquidacionFilters) {
  const { data } = await api.get<{ items: Liquidacion[]; total: number }>('/liquidaciones/historial', { params: filters })
  return data
}

export async function listarSalariosBase() {
  const { data } = await api.get<SalarioBase[]>('/liquidaciones/grilla/bases')
  return data
}

export async function crearSalarioBase(payload: SalarioBasePayload) {
  const { data } = await api.post<SalarioBase>('/liquidaciones/grilla/bases', payload)
  return data
}

export async function actualizarSalarioBase(id: string, payload: Partial<SalarioBasePayload>) {
  const { data } = await api.patch<SalarioBase>(`/liquidaciones/grilla/bases/${id}`, payload)
  return data
}

export async function listarPlus() {
  const { data } = await api.get<Plus[]>('/liquidaciones/grilla/pluses')
  return data
}

export async function crearPlus(payload: PlusPayload) {
  const { data } = await api.post<Plus>('/liquidaciones/grilla/pluses', payload)
  return data
}

export async function actualizarPlus(id: string, payload: Partial<PlusPayload>) {
  const { data } = await api.patch<Plus>(`/liquidaciones/grilla/pluses/${id}`, payload)
  return data
}

export async function listarFacturas(filters?: FacturaFilters) {
  const { data } = await api.get<{ items: Factura[]; total: number }>('/facturas', { params: filters })
  return data
}

export async function crearFactura(payload: FacturaPayload) {
  const { data } = await api.post<Factura>('/facturas', payload)
  return data
}

export async function cambiarEstadoFactura(id: string, estado: 'pendiente' | 'abonada') {
  const { data } = await api.patch<Factura>(`/facturas/${id}/estado`, { estado })
  return data
}
