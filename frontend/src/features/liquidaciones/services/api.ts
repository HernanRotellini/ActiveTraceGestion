import api from '@/shared/services/api'
import type {
  SalarioBaseResponse,
  SalarioBaseCreate,
  SalarioBaseUpdate,
  SalarioPlusResponse,
  SalarioPlusCreate,
  MateriaPlusResponse,
  MateriaPlusCreate,
  LiquidacionPreviewRequest,
  LiquidacionPreviewResponse,
  LiquidacionCloseRequest,
  LiquidacionResponse,
  LiquidacionFilters,
  FacturaResponse,
  FacturaCreate,
  FacturaUpdate,
  FacturaFilters,
} from '@/features/liquidaciones/types'

export async function listarSalariosBase() {
  const { data } = await api.get<SalarioBaseResponse[]>('/api/liquidaciones/grilla/bases')
  return data
}

export async function crearSalarioBase(payload: SalarioBaseCreate) {
  const { data } = await api.post<SalarioBaseResponse>('/api/liquidaciones/grilla/bases', payload)
  return data
}

export async function actualizarSalarioBase(id: string, payload: SalarioBaseUpdate) {
  const { data } = await api.put<SalarioBaseResponse>(`/api/liquidaciones/grilla/bases/${id}`, payload)
  return data
}

export async function eliminarSalarioBase(id: string) {
  await api.delete(`/api/liquidaciones/grilla/bases/${id}`)
}

export async function listarPlus() {
  const { data } = await api.get<SalarioPlusResponse[]>('/api/liquidaciones/grilla/pluses')
  return data
}

export async function crearPlus(payload: SalarioPlusCreate) {
  const { data } = await api.post<SalarioPlusResponse>('/api/liquidaciones/grilla/pluses', payload)
  return data
}

export async function listarMateriaPlus() {
  const { data } = await api.get<MateriaPlusResponse[]>('/api/liquidaciones/grilla/materia-plus')
  return data
}

export async function crearMateriaPlus(payload: MateriaPlusCreate) {
  const { data } = await api.post<MateriaPlusResponse>('/api/liquidaciones/grilla/materia-plus', payload)
  return data
}

export async function previewLiquidacion(payload: LiquidacionPreviewRequest) {
  const { data } = await api.post<LiquidacionPreviewResponse>('/api/liquidaciones/preview', payload)
  return data
}

export async function cerrarLiquidacion(payload: LiquidacionCloseRequest) {
  const { data } = await api.post<LiquidacionResponse[]>('/api/liquidaciones/cerrar', payload)
  return data
}

export async function listarLiquidaciones(filters?: LiquidacionFilters) {
  const { data } = await api.get<LiquidacionResponse[]>('/api/liquidaciones', { params: filters })
  return data
}

export async function obtenerLiquidacion(id: string) {
  const { data } = await api.get<LiquidacionResponse>(`/api/liquidaciones/${id}`)
  return data
}

export async function listarFacturas(filters?: FacturaFilters) {
  const { data } = await api.get<FacturaResponse[]>('/api/facturas', { params: filters })
  return data
}

export async function obtenerFactura(id: string) {
  const { data } = await api.get<FacturaResponse>(`/api/facturas/${id}`)
  return data
}

export async function crearFactura(payload: FacturaCreate) {
  const { data } = await api.post<FacturaResponse>('/api/facturas', payload)
  return data
}

export async function actualizarFactura(id: string, payload: FacturaUpdate) {
  const { data } = await api.put<FacturaResponse>(`/api/facturas/${id}`, payload)
  return data
}

export async function eliminarFactura(id: string) {
  await api.delete(`/api/facturas/${id}`)
}

export async function marcarFacturaAbonada(id: string) {
  const { data } = await api.post<FacturaResponse>(`/api/facturas/${id}/abonada`)
  return data
}
