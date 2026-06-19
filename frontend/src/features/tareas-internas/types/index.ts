export type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'

export interface ComentarioResponse {
  id: string
  tarea_id: string
  autor_id: string
  texto: string
  created_at: string
}

export interface TareaResponse {
  id: string
  titulo: string
  descripcion: string
  estado: TareaEstado
  asignado_a: string
  asignado_por: string
  materia_id: string | null
  contexto_id: string | null
  created_at: string
  updated_at: string
}

export interface TareaDetailResponse extends TareaResponse {
  comentarios: ComentarioResponse[]
}

export interface TareaPayload {
  titulo: string
  descripcion: string
  asignado_a: string
  materia_id?: string
  contexto_id?: string
}

export interface ComentarioPayload {
  texto: string
}

export interface TareasFilters {
  asignado_a?: string
  asignado_por?: string
  materia_id?: string
  estado?: TareaEstado
  search?: string
  limit?: number
  offset?: number
}
