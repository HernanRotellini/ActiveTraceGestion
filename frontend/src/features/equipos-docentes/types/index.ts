export interface EquipoDocente {
  id: string
  materia_id: string
  materia_nombre: string
  carrera: string
  estado: 'activo' | 'inactivo'
  creado_en: string
  actualizado_en: string
  asignaciones: Asignacion[]
}

export interface Asignacion {
  id: string
  equipo_id: string
  usuario_id: string
  usuario_nombre: string
  rol: 'titular' | 'adjunto' | 'auxiliar' | 'jefe_tp'
  activo: boolean
  desde: string
  hasta?: string
}

export interface AsignacionMasivaPayload {
  equipo_id: string
  usuarios: Array<{
    usuario_id: string
    rol: Asignacion['rol']
  }>
}

export interface ClonePayload {
  origen_equipo_id: string
  destino_materia_id: string
  periodo: string
}

export interface VigenciaPayload {
  asignacion_id: string
  desde: string
  hasta?: string
}

export interface EquiposFilters {
  materia?: string
  carrera?: string
  estado?: string
  page?: number
  limit?: number
}
