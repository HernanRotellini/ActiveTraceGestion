export interface Calificacion {
  id: string
  alumno_id: string
  alumno_nombre: string
  materia: string
  nota: number | null
  estado: 'aprobado' | 'desaprobado' | 'sin_nota'
  fecha_importacion: string
}

export interface ActividadDetectada {
  actividad_id: string
  nombre: string
  tipo: string
  fecha: string
  calificaciones_count: number
  seleccionada: boolean
}

export interface UmbralConfig {
  id: string
  nota_maxima: number
  nota_minima: number
  umbral_atraso: number
  umbral_promocion: number
}

export interface AtrasadosResponse {
  total: number
  items: Array<{
    alumno_id: string
    alumno_nombre: string
    materia: string
    atraso_dias: number
    ultima_actividad: string | null
  }>
}

export interface RankingItem {
  alumno_id: string
  alumno_nombre: string
  promedio: number
  puesto: number
  total_actividades: number
}

export interface NotasFinalesItem {
  alumno_id: string
  alumno_nombre: string
  nota_final: number | null
  condicion: 'promocionado' | 'regular' | 'libre'
}
