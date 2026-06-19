export interface Carrera {
  id: string
  nombre: string
  codigo: string
  descripcion?: string
  estado: 'activa' | 'inactiva'
  activo: boolean
  creada_en: string
}

export interface CarreraPayload {
  nombre: string
  codigo: string
  descripcion?: string
  estado?: 'activa' | 'inactiva'
}

export type CarreraUpdatePayload = Partial<CarreraPayload>

export interface CarreraFilters {
  codigo?: string
  nombre?: string
  estado?: 'activa' | 'inactiva'
}

export interface Cohorte {
  id: string
  carrera_id: string
  nombre: string
  anio: number
  vig_desde: string
  vig_hasta?: string | null
  estado: 'activa' | 'inactiva'
  activo: boolean
  creada_en: string
}

export interface CohortePayload {
  carrera_id: string
  nombre: string
  anio: number
  vig_desde: string
  vig_hasta?: string
  estado?: 'activa' | 'inactiva'
}

export type CohorteUpdatePayload = Partial<Omit<CohortePayload, 'carrera_id' | 'vig_hasta'>> & {
  vig_hasta?: string | null
}

export interface Materia {
  id: string
  carrera_id: string | null
  cohorte_id: string | null
  nombre: string
  codigo: string
  carga_horaria: number
  estado: 'activa' | 'inactiva'
  activo: boolean
  creada_en: string
  carrera_nombre?: string
  cohorte_nombre?: string
}

export interface MateriaPayload {
  nombre: string
  codigo: string
  carrera_id?: string
  cohorte_id?: string
  carga_horaria?: number
  estado?: 'activa' | 'inactiva'
}

export type MateriaUpdatePayload = Partial<MateriaPayload>

export interface UsuarioAdmin {
  id: string
  nombre: string
  apellidos: string
  email: string
  dni?: string
  cuil?: string
  cbu?: string
  alias_cbu?: string
  telefono?: string
  direccion?: string
  estado: string
  legajo?: string
  banco?: string
  facturador: boolean
  roles?: string[]
  created_at: string
  updated_at?: string
}

export interface UsuarioAdminPayload {
  nombre: string
  apellidos: string
  email: string
  dni?: string
  cuil?: string
  cbu?: string
  alias_cbu?: string
  telefono?: string
  direccion?: string
  legajo?: string
  banco?: string
  facturador?: boolean
}

export interface UsuarioAdminFilters {
  nombre?: string
  email?: string
}

export interface AccionesPorDia {
  fecha: string
  total: number
}

export interface ComunicacionPorDocente {
  docente_id: string
  accion: string
  total: number
}

export interface Interaccion {
  docente_id: string
  materia_id: string | null
  accion: string
  total: number
}

export interface UltimaAccion {
  id: string
  tenant_id: string
  fecha_hora: string
  actor_id: string
  impersonado_id: string | null
  materia_id: string | null
  accion: string
  detalle: Record<string, unknown> | null
  filas_afectadas: number | null
  ip: string | null
  user_agent: string | null
}

export interface AuditoriaEntry {
  id: string
  tenant_id: string
  fecha_hora: string
  actor_id: string
  impersonado_id: string | null
  materia_id: string | null
  accion: string
  detalle: Record<string, unknown> | null
  filas_afectadas: number | null
  ip: string | null
  user_agent: string | null
}

export interface AuditoriaFilters {
  fecha_desde?: string
  fecha_hasta?: string
  actor_id?: string
  accion?: string
  materia_id?: string
  limit?: number
  offset?: number
}
