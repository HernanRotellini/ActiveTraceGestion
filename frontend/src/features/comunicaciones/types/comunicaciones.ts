// Estados reales del backend (app/models/comunicacion.py · EstadoComunicacion).
export type EstadoComunicacion =
  | 'Pendiente'
  | 'Enviando'
  | 'Enviado'
  | 'Error'
  | 'Cancelado'

export interface PreviewRequest {
  asunto: string
  cuerpo: string
  variables?: Record<string, string>
}

export interface PreviewResponse {
  asunto_renderizado: string
  cuerpo_renderizado: string
}

export interface MateriaOption {
  id: string
  nombre: string
  codigo?: string
}

export interface EnvioMasivoRequest {
  materia_id: string
  asunto: string
  cuerpo: string
}

export interface EnvioMasivoResponse {
  lote_id: string
  mensajes_creados: number
}

export interface LoteResumen {
  lote_id: string
  materia_id: string
  total: number
  pendientes: number
  enviados: number
  errores: number
  cancelados: number
  created_at: string
}

export interface LotesListResponse {
  items: LoteResumen[]
  total: number
}

export interface ComunicacionDetail {
  id: string
  materia_id: string
  destinatario: string
  asunto: string
  cuerpo: string
  estado: EstadoComunicacion
  lote_id: string
  enviado_at?: string | null
  created_at: string
  updated_at: string
}

export interface LoteDetalleResponse {
  lote_id: string
  materia_id: string
  comunicaciones: ComunicacionDetail[]
}

export interface AccionResponse {
  mensaje: string
  afectados: number
}

// Variables que el backend sustituye por alumno (comunicacion_service.VARIABLES_SOPORTADAS).
export const VARIABLES_SOPORTADAS = ['nombre', 'apellido', 'materia', 'comision'] as const
