export type AvisoAlcance = 'Global' | 'PorMateria' | 'PorCohorte' | 'PorRol'
export type AvisoSeveridad = 'Info' | 'Advertencia' | 'Critico'

// Legacy scope values used by the form (mapped to AvisoAlcance before sending)
export type AvisoScope = 'todos' | 'por_rol' | 'por_comision' | 'por_usuario'

export interface AckStatus {
  usuario_id: string
  usuario_nombre: string
  leido: boolean
  leido_en?: string
}

export interface Aviso {
  id: string
  titulo: string
  cuerpo: string
  alcance: AvisoAlcance
  severidad: AvisoSeveridad
  activo: boolean
  requiere_ack: boolean
  inicio_en: string
  fin_en?: string
  orden: number
  created_at: string
  // Solo en AvisoResponse (admin)
  materia_id?: string
  cohorte_id?: string
  rol_destino?: string
  updated_at?: string
  // Campos de la respuesta admin completa
  estado?: string
  autor_nombre?: string
  publicado_en?: string
  acks?: AckStatus[]
  // Alias para compatibilidad con páginas legacy
  contenido?: string
  scope?: string
  scope_valor?: string
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
  activo?: string
  page?: number
  limit?: number
}

// Legacy filter type — kept for compatibility
export interface AvisosListFilters {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
