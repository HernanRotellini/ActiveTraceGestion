export interface TurnoCreate {
  fecha: string
  hora_inicio?: string
  hora_fin?: string
  cupo_maximo: number
}

export interface TurnoResponse {
  id: string
  evaluacion_id: string
  fecha: string
  hora_inicio: string | null
  hora_fin: string | null
  cupo_maximo: number
  cupo_restante: number
}

export interface EvaluacionCreate {
  materia_id: string
  cohorte_id: string
  tipo: string
  instancia: string
  turnos: TurnoCreate[]
}

export interface EvaluacionResponse {
  id: string
  materia_id: string
  cohorte_id: string
  tipo: string
  instancia: string
  estado: string
  turnos: TurnoResponse[]
  created_at: string
  updated_at: string
}

export interface EvaluacionListResponse {
  id: string
  materia_id: string
  cohorte_id: string
  tipo: string
  instancia: string
  estado: string
  total_turnos: number
  alumnos_convocados: number
  reservas_activas: number
  cupos_libres: number
  created_at: string
}

export interface ReservaResponse {
  id: string
  evaluacion_id: string
  turno_id: string
  alumno_id: string
  estado: string
  created_at: string
}

export interface ResultadoCreate {
  alumno_id: string
  nota_final: string
}

export interface ResultadoResponse {
  id: string
  evaluacion_id: string
  alumno_id: string
  nota_final: string
  registrado_por: string
  created_at: string
  updated_at: string
}

export interface MetricasColoquiosResponse {
  alumnos_convocados: number
  convocatorias_activas: number
  reservas_activas: number
  notas_registradas: number
}

export interface AgendaReservaResponse {
  id: string
  evaluacion_id: string
  turno_id: string
  fecha: string | null
  alumno_id: string
  created_at: string
}

export interface ColoquiosFilters {
  materia_id?: string
}
