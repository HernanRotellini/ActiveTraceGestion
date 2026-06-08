export interface Encuentro {
  id: string
  comision_id: string
  comision_nombre: string
  materia_nombre: string
  fecha: string
  duracion_minutos: number
  aula: string
  tema?: string
  slots: SlotHorario[]
  instancias: InstanciaDictado[]
  guardias: Guardia[]
  creado_en: string
}

export interface SlotHorario {
  id: string
  encuentro_id: string
  hora_inicio: string
  hora_fin: string
  docente_id?: string
  docente_nombre?: string
  tema?: string
}

export interface InstanciaDictado {
  id: string
  encuentro_id: string
  materia_id: string
  materia_nombre: string
  comision_id: string
  comision_nombre: string
  docente_id: string
  docente_nombre: string
}

export interface Guardia {
  id: string
  encuentro_id: string
  docente_id: string
  docente_nombre: string
  hora_inicio: string
  hora_fin: string
}

export interface EncuentrosFilters {
  fecha_desde?: string
  fecha_hasta?: string
  materia_id?: string
  comision_id?: string
  page?: number
  limit?: number
}

export interface EncuentroPayload {
  comision_id: string
  fecha: string
  duracion_minutos: number
  aula: string
  tema?: string
}
