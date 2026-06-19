export type AvisoAlcance = 'Global' | 'PorMateria' | 'PorCohorte' | 'PorRol'
export type AvisoSeveridad = 'Info' | 'Advertencia' | 'Critico'

export interface AvisoResponse {
  id: string
  tenant_id: string
  alcance: AvisoAlcance
  materia_id: string | null
  cohorte_id: string | null
  rol_destino: string | null
  severidad: AvisoSeveridad
  titulo: string
  cuerpo: string
  inicio_en: string
  fin_en: string | null
  orden: number
  activo: boolean
  requiere_ack: boolean
  created_at: string
  updated_at: string
}

export interface AvisoListResponse {
  id: string
  alcance: AvisoAlcance
  severidad: AvisoSeveridad
  titulo: string
  inicio_en: string
  fin_en: string | null
  orden: number
  requiere_ack: boolean
  created_at: string
}

export interface AvisoStatsResponse {
  total_acks: number
  usuarios_sin_confirmar: string[] | null
}

export interface AvisoPayload {
  titulo: string
  cuerpo: string
  alcance: AvisoAlcance
  severidad?: AvisoSeveridad
  materia_id?: string
  cohorte_id?: string
  rol_destino?: string
  inicio_en: string
  fin_en?: string
  orden?: number
  activo?: boolean
  requiere_ack?: boolean
}

export interface AvisosFilters {
  alcance?: string
  severidad?: string
  activo?: boolean
}
