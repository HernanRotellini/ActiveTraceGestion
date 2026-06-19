export interface Calificacion {
  id: string
  tenant_id: string
  entrada_padron_id: string
  materia_id: string
  actividad: string
  nota_numerica: number | null
  nota_textual: string | null
  aprobado: boolean
  origen: string
  importado_at: string | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface CalificacionesResponse {
  items: Calificacion[]
  total: number
}

export interface ActividadDetectada {
  nombre: string
  tipo: string
}

export interface ImportPreviewResponse {
  preview_token: string
  materia_id: string
  cohorte_id: string
  actividades: ActividadDetectada[]
  total_rows: number
  alumnos_match: Array<{
    entrada_padron_id: string
    nombre: string
    apellidos: string
    email: string
    datos: Record<string, string | number | null>
  }>
  alumnos_no_match: Array<{
    fila: number
    datos: Record<string, string>
  }>
}

export interface ImportConfirmResponse {
  materia_id: string
  cohorte_id: string
  registros_creados: number
  actividades_importadas: string[]
}

export interface UmbralConfig {
  id: string
  tenant_id: string
  asignacion_id: string
  materia_id: string
  umbral_pct: number
  valores_aprobatorios: string[] | null
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface AtrasadoItem {
  entrada_padron_id: string
  alumno_nombre: string
  actividades_atrasadas: Array<{
    actividad: string
    motivo: string
  }>
}

export interface RankingItem {
  ranking: number
  entrada_padron_id: string
  alumno_nombre: string
  actividades_aprobadas: number
}

export interface RankingResponse {
  items: RankingItem[]
  total: number
}

export interface NotaFinalItem {
  entrada_padron_id: string
  alumno_nombre: string
  promedio: number
  aprobado: boolean
}

export interface NotasFinalesResponse {
  items: NotaFinalItem[]
  total: number
}

export interface ReportesRapidosResponse {
  total_alumnos: number
  total_calificaciones: number
  promedio_general: number
  total_aprobados: number
  total_no_aprobados: number
  desglose_por_actividad: Array<{
    actividad: string
    presentado: number
    promedio: number | null
    min: number | null
    max: number | null
  }>
}
