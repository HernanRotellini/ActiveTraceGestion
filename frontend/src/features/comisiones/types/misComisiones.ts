export interface MisComisionesItem {
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
  materia_nombre?: string | null
  carrera_nombre?: string | null
  cohorte_nombre?: string | null
}

export interface MisComisionesFilters {
  estado?: 'vigente' | 'vencida'
  materia_id?: string
  carrera_id?: string
  cohorte_id?: string
  rol?: string
}
