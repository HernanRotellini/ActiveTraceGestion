export type AvisoScope = 'todos' | 'por_rol' | 'por_comision' | 'por_usuario'

export type AvisoEstado = 'borrador' | 'publicado' | 'archivado'

export interface Aviso {
  id: string
  titulo: string
  contenido: string
  scope: AvisoScope
  scope_valor?: string
  estado: AvisoEstado
  creado_en: string
  publicado_en?: string
  autor_id: string
  autor_nombre: string
  acks: AckStatus[]
}

export interface AckStatus {
  usuario_id: string
  usuario_nombre: string
  leido: boolean
  leido_en?: string
}

export interface AvisoPayload {
  titulo: string
  contenido: string
  scope: AvisoScope
  scope_valor?: string
}

export interface AvisosFilters {
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
