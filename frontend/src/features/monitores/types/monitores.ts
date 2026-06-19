export interface MonitorFilters {
  materia_id?: string
  busqueda?: string
  regional?: string
  comision?: string
  actividad?: string
  min_actividad_cumplida?: number
  page?: number
  per_page?: number
  periodo?: string
}

export interface MonitorItem {
  entrada_padron_id: string
  alumno_nombre: string
  email: string
  regional: string | null
  comision: string | null
  total_actividades: number
  aprobadas: number
  pendientes: number
  atrasado: boolean
}

export interface MonitorResponse {
  items: MonitorItem[]
  total: number
}
