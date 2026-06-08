export interface Carrera {
  id: string
  nombre: string
  codigo: string
  descripcion?: string
  activo: boolean
  creada_en: string
}

export interface CarreraPayload {
  nombre: string
  codigo: string
  descripcion?: string
  activo?: boolean
}

export interface Cohorte {
  id: string
  carrera_id: string
  nombre: string
  anio: number
  activo: boolean
  creada_en: string
}

export interface CohortePayload {
  carrera_id: string
  nombre: string
  anio: number
  activo?: boolean
}

export interface Materia {
  id: string
  carrera_id: string
  cohorte_id: string
  nombre: string
  codigo: string
  carga_horaria: number
  activo: boolean
  creada_en: string
  carrera_nombre?: string
  cohorte_nombre?: string
}

export interface MateriaPayload {
  carrera_id: string
  cohorte_id: string
  nombre: string
  codigo: string
  carga_horaria: number
  activo?: boolean
}

export interface UsuarioAdmin {
  id: string
  nombre: string
  email: string
  dni?: string
  cbu?: string
  roles: string[]
  activo: boolean
  creado_en: string
}

export interface UsuarioAdminPayload {
  nombre: string
  email: string
  password: string
  dni?: string
  cbu?: string
  roles: string[]
  activo?: boolean
}

export interface UsuarioAdminFilters {
  nombre?: string
  email?: string
  rol?: string
  page?: number
  limit?: number
}

export interface ActionByDay {
  fecha: string
  total: number
}

export interface ComunicacionEstado {
  docente_id: string
  docente_nombre: string
  enviadas: number
  pendientes: number
  fallidas: number
}

export interface Interaccion {
  docente_id: string
  docente_nombre: string
  materia: string
  total: number
}

export interface MetricasDashboard {
  acciones_por_dia: ActionByDay[]
  comunicaciones: ComunicacionEstado[]
  interacciones: Interaccion[]
  total_acciones: number
  total_comunicaciones: number
}

export interface AuditoriaEntry {
  id: string
  fecha_hora: string
  usuario: string
  materia?: string
  accion: string
  registros_afectados: number
  ip_origen?: string
  user_agent?: string
  detalle?: string
}

export interface AuditoriaFilters {
  usuario?: string
  materia?: string
  accion?: string
  fecha_desde?: string
  fecha_hasta?: string
  page?: number
  limit?: number
}
