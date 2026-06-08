export type TareaEstado = 'pendiente' | 'en_progreso' | 'completada' | 'cancelada'

export type Prioridad = 'baja' | 'media' | 'alta' | 'critica'

export interface Tarea {
  id: string
  titulo: string
  descripcion: string
  estado: TareaEstado
  prioridad: Prioridad
  asignado_id?: string
  asignado_nombre?: string
  creador_id: string
  creador_nombre: string
  fecha_limite?: string
  creado_en: string
  actualizado_en: string
  comentarios: Comentario[]
}

export interface Comentario {
  id: string
  tarea_id: string
  autor_id: string
  autor_nombre: string
  contenido: string
  creado_en: string
  padre_id?: string
}

export interface TareaPayload {
  titulo: string
  descripcion: string
  prioridad: Prioridad
  asignado_id?: string
  fecha_limite?: string
}

export interface ComentarioPayload {
  contenido: string
  padre_id?: string
}

export interface TareasFilters {
  estado?: string
  asignado_id?: string
  prioridad?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
