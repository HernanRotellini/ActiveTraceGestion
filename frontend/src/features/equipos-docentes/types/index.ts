export type RolAsignacionDocente = 'PROFESOR' | 'TUTOR' | 'COORDINADOR' | 'NEXO'

export interface Asignacion {
  id: string
  usuario_id: string
  usuario_nombre: string
  rol: RolAsignacionDocente
  activo: boolean
  desde: string
  hasta?: string
}

export interface ClonePayload {
  origen: {
    materia_id: string
    carrera_id: string
    cohorte_id: string
  }
  destino: {
    carrera_id: string
    cohorte_id: string
    desde: string
    hasta?: string
  }
}

export interface VigenciaPayload {
  materia_id: string
  carrera_id: string
  cohorte_id: string
  desde?: string
  hasta?: string
}

export interface CrearAsignacionesEquipoPayload {
  usuario_ids: string[]
  materia_id: string
  carrera_id: string
  cohorte_id: string
  rol: RolAsignacionDocente
  comisiones?: string[]
  desde: string
  hasta?: string
}

export interface AsignacionEquipoResponse {
  id: string
  usuario_id: string
  rol: string
  materia_id: string | null
  carrera_id: string | null
  cohorte_id: string | null
  comisiones: string[] | null
  responsable_id: string | null
  desde: string
  hasta: string | null
  estado_vigencia: 'vigente' | 'vencida'
  created_at: string
  updated_at: string
}

export interface AsignacionListFilters {
  materia_id?: string
  usuario_id?: string
  rol?: string
}

export interface ExportarEquiposParams {
  materia_id: string
  carrera_id: string
  cohorte_id: string
}
