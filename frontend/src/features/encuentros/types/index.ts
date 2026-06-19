export type EstadoInstancia = 'Programado' | 'Realizado' | 'Cancelado'

export type DiaSemana = 'Lunes' | 'Martes' | 'Miercoles' | 'Jueves' | 'Viernes' | 'Sabado'

export interface SlotEncuentroResponse {
  id: string
  asignacion_id: string
  materia_id: string
  titulo: string
  dia_semana: DiaSemana
  hora: string
  fecha_inicio: string
  cant_semanas: number
  fecha_unica: string | null
  meet_url: string | null
  vig_desde: string
  vig_hasta: string | null
  created_at: string
  updated_at: string
}

export interface SlotEncuentroPayload {
  asignacion_id: string
  materia_id: string
  titulo: string
  dia_semana: DiaSemana
  hora: string
  fecha_inicio: string
  cant_semanas?: number
  meet_url?: string
  vig_desde: string
  vig_hasta?: string
}

export interface InstanciaEncuentroResponse {
  id: string
  slot_id: string | null
  materia_id: string
  fecha: string
  hora: string
  titulo: string
  estado: EstadoInstancia
  meet_url: string | null
  video_url: string | null
  comentario: string | null
  created_at: string
  updated_at: string
}

export interface InstanciaEncuentroPayload {
  materia_id: string
  fecha: string
  hora: string
  titulo: string
  meet_url?: string
}

export interface InstanciaEncuentroUpdate {
  estado?: EstadoInstancia
  meet_url?: string
  video_url?: string
  comentario?: string
}

export interface EncuentrosFilters {
  materia_id?: string
}

export interface AdminInstanciasFilters {
  materia_id?: string
  fecha_desde?: string
  fecha_hasta?: string
  estado?: EstadoInstancia
}
