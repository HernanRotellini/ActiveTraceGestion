export type ResultadoColoquio = 'pendiente' | 'aprobado' | 'desaprobado' | 'ausente'

export interface EvaluacionColoquio {
  id: string
  materia_id: string
  materia_nombre: string
  comision_id: string
  comision_nombre: string
  fecha: string
  aula: string
  estado: 'programado' | 'en_curso' | 'finalizado'
  observaciones?: string
  reservas: Reserva[]
  creado_en: string
}

export interface Reserva {
  id: string
  coloquio_id: string
  alumno_id: string
  alumno_nombre: string
  confirmado: boolean
  resultado: ResultadoColoquio
  nota?: number
  observaciones?: string
}

export interface ColoquioPayload {
  materia_id: string
  comision_id: string
  fecha: string
  aula: string
  observaciones?: string
}

export interface ColoquiosFilters {
  materia_id?: string
  comision_id?: string
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
