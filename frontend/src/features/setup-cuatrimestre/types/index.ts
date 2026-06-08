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
