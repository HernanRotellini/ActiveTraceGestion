export interface LiquidacionItem {
  id: string
  liquidacion_id: string
  docente_id: string
  docente_nombre: string
  materia: string
  comision: string
  rol: string
  horas: number
  valor_hora: number
  subtotal: number
  segmento: 'general' | 'nexo' | 'factura'
}

export interface Liquidacion {
  id: string
  periodo: string
  cohorte_id: string
  cohorte_nombre: string
  estado: 'abierta' | 'cerrada'
  total_general: number
  total_nexo: number
  total_factura: number
  items: LiquidacionItem[]
  cerrada_en?: string
  creada_en: string
}

export interface LiquidacionFilters {
  cohorte_id?: string
  mes?: string
  docente?: string
  page?: number
  limit?: number
}

export interface SalarioBase {
  id: string
  rol: string
  importe: number
  vigencia_desde: string
  vigencia_hasta?: string
  activo: boolean
}

export interface SalarioBasePayload {
  rol: string
  importe: number
  vigencia_desde: string
  vigencia_hasta?: string
}

export interface Plus {
  id: string
  clave: string
  rol: string
  descripcion: string
  importe: number
  vigencia_desde: string
  vigencia_hasta?: string
  activo: boolean
}

export interface PlusPayload {
  clave: string
  rol: string
  descripcion: string
  importe: number
  vigencia_desde: string
  vigencia_hasta?: string
}

export interface Factura {
  id: string
  docente_id: string
  docente_nombre: string
  periodo: string
  importe: number
  estado: 'pendiente' | 'abonada'
  creada_en: string
  abonada_en?: string
  observaciones?: string
}

export interface FacturaPayload {
  docente_id: string
  periodo: string
  importe: number
  observaciones?: string
}

export interface FacturaFilters {
  docente?: string
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  q?: string
  page?: number
  limit?: number
}
