export interface MonitorFilters {
  comision_id?: string
  materia_id?: string
  estado?: string
  fecha_desde?: string
  fecha_hasta?: string
}

export interface MonitorAlumno {
  alumno_id: string
  alumno_nombre: string
  comision: string
  materia: string
  actividades_pendientes: number
  entregas_sin_corregir: number
  promedio_actual: number | null
  asistencias: number
  estado: 'al_dia' | 'atrasado' | 'critico'
  ultima_actividad: string | null
}
