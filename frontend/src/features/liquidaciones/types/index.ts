export type RolLiquidacion = 'PROFESOR' | 'TUTOR' | 'NEXO' | 'COORDINADOR'
export type EstadoLiquidacion = 'Abierta' | 'Cerrada'
export type EstadoFactura = 'Pendiente' | 'Abonada'
export type SegmentoLiquidacion = 'general' | 'nexo' | 'facturante'

export interface SalarioBaseResponse {
  id: string
  rol: RolLiquidacion
  monto: string
  desde: string
  hasta: string | null
  created_at: string
}

export interface SalarioBaseCreate {
  rol: RolLiquidacion
  monto: string
  desde: string
  hasta?: string
}

export interface SalarioBaseUpdate {
  rol?: RolLiquidacion
  monto?: string
  desde?: string
  hasta?: string | null
}

export interface SalarioPlusResponse {
  id: string
  rol: RolLiquidacion
  grupo: string
  descripcion: string
  monto: string
  desde: string
  hasta: string | null
  created_at: string
}

export interface SalarioPlusCreate {
  rol: RolLiquidacion
  grupo: string
  descripcion: string
  monto: string
  desde: string
  hasta?: string
}

export interface MateriaPlusResponse {
  id: string
  materia_id: string
  grupo: string
  desde: string
  hasta: string | null
  created_at: string
}

export interface MateriaPlusCreate {
  materia_id: string
  grupo: string
  desde: string
  hasta?: string
}

export interface LiquidacionPreviewItem {
  usuario_id: string
  rol: RolLiquidacion
  monto_base: string
  monto_plus: string
  monto_total: string
  comisiones: string[]
  es_nexo: boolean
  excluido_por_factura: boolean
  procesable: boolean
  motivo_no_procesable: string | null
}

export interface LiquidacionPreviewResponse {
  cohorte_id: string
  periodo: string
  items: LiquidacionPreviewItem[]
  total_pagable: string
  segmento_nexo_total: string
  segmento_facturantes_total: string
}

export interface LiquidacionPreviewRequest {
  cohorte_id: string
  periodo: string
}

export interface LiquidacionCloseRequest {
  cohorte_id: string
  periodo: string
}

export interface LiquidacionResponse {
  id: string
  cohorte_id: string
  usuario_id: string
  periodo: string
  rol: RolLiquidacion
  estado: EstadoLiquidacion
  monto_base: string
  monto_plus: string
  monto_total: string
  comisiones: string[]
  es_nexo: boolean
  excluido_por_factura: boolean
  created_at: string
}

export interface LiquidacionFilters {
  periodo?: string
  cohorte_id?: string
  usuario_id?: string
  segmento?: SegmentoLiquidacion
}

export interface FacturaResponse {
  id: string
  usuario_id: string
  periodo: string
  detalle: string
  referencia_archivo: string
  archivo_size_bytes: number
  estado: EstadoFactura
  abonada_at: string | null
  created_at: string
}

export interface FacturaCreate {
  usuario_id: string
  periodo: string
  detalle: string
  referencia_archivo: string
  archivo_size_bytes: number
}

export interface FacturaUpdate {
  periodo?: string
  detalle?: string
  referencia_archivo?: string
  archivo_size_bytes?: number
}

export interface FacturaFilters {
  usuario_id?: string
  periodo?: string
  estado?: EstadoFactura
  desde?: string
  hasta?: string
}
