export interface PeriodoAcademico {
  id: string
  nombre: string
  fecha_inicio: string
  fecha_fin: string
  activo: boolean
  fechas: FechaAcademica[]
  programas: ProgramaMateria[]
}

export interface FechaAcademica {
  id: string
  periodo_id: string
  key: string
  label: string
  fecha: string
}

export interface ProgramaMateria {
  id: string
  periodo_id: string
  materia_id: string
  materia_nombre: string
  carrera: string
  anio: number
  activo: boolean
}

export interface PeriodoPayload {
  nombre: string
  fecha_inicio: string
  fecha_fin: string
}

export interface FechaPayload {
  key: string
  label: string
  fecha: string
}

export interface ProgramaPayload {
  materia_id: string
  carrera: string
  anio: number
}

export interface ProgramaOficial {
  id: string
  materia_id: string
  carrera_id: string
  cohorte_id: string
  titulo: string
  referencia_archivo: string
  created_at: string
}

export interface ProgramaOficialPayload {
  materia_id: string
  carrera_id: string
  cohorte_id: string
  titulo: string
  referencia_archivo: string
}

export interface ProgramaOficialUpdatePayload {
  titulo?: string
  referencia_archivo?: string
}

export type TipoFechaAcademica = 'Parcial' | 'TP' | 'Coloquio' | 'Recuperatorio'

export interface FechaAcademicaOficial {
  id: string
  materia_id: string
  cohorte_id: string
  tipo: TipoFechaAcademica
  numero: number
  periodo: string
  fecha: string
  titulo: string
  created_at: string
}

export interface FechaAcademicaOficialPayload {
  materia_id: string
  cohorte_id: string
  tipo: TipoFechaAcademica
  numero: number
  periodo: string
  fecha: string
  titulo: string
}

export interface FechaAcademicaOficialUpdatePayload {
  titulo?: string
  fecha?: string
  numero?: number
  periodo?: string
}
