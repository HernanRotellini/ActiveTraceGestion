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
  const { data } = await api.get<SalarioBase[]>('/grilla-salarial/salarios-base')
  return data
}

export async function crearSalarioBase(payload: SalarioBasePayload) {
  const { data } = await api.post<SalarioBase>('/grilla-salarial/salarios-base', payload)
  return data
}

export async function actualizarSalarioBase(id: string, payload: Partial<SalarioBasePayload>) {
  const { data } = await api.patch<SalarioBase>(`/grilla-salarial/salarios-base/${id}`, payload)
  return data
}

export async function listarPlus() {
  const { data } = await api.get<Plus[]>('/grilla-salarial/plus')
  return data
}

export async function crearPlus(payload: PlusPayload) {
  const { data } = await api.post<Plus>('/grilla-salarial/plus', payload)
  return data
}

export async function actualizarPlus(id: string, payload: Partial<PlusPayload>) {
  const { data } = await api.patch<Plus>(`/grilla-salarial/plus/${id}`, payload)
  return data
}

export async function listarFacturas(filters?: FacturaFilters) {
  const { data } = await api.get<{ items: Factura[]; total: number }>('/facturas-docentes', { params: filters })
  return data
}

export async function crearFactura(payload: FacturaPayload) {
  const { data } = await api.post<Factura>('/facturas-docentes', payload)
  return data
}

export async function cambiarEstadoFactura(id: string, estado: 'pendiente' | 'abonada') {
  const { data } = await api.patch<Factura>(`/facturas-docentes/${id}/estado`, { estado })
  return data
}
