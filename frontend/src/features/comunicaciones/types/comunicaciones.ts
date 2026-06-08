export type EstadoComunicacion = 'pendiente' | 'enviado' | 'fallido' | 'cancelado'

export interface PreviewRequest {
  tipo: string
  destinatarios: string[]
  template: string
  variables?: Record<string, string>
}

export interface PreviewResponse {
  asunto: string
  cuerpo: string
  destinatarios_count: number
}

export interface EnvioRequest {
  comision_id: string
  tipo: string
  asunto: string
  cuerpo: string
  destinatarios: string[]
  programar_para?: string
}

export interface EnvioResponse {
  envio_id: string
  estado: EstadoComunicacion
  total_destinatarios: number
}

export interface TrackingComunicacion {
  envio_id: string
  asunto: string
  estado: EstadoComunicacion
  enviados: number
  total: number
  fecha_envio: string
  destinatarios: Array<{
    email: string
    nombre: string
    estado: EstadoComunicacion
    error?: string
  }>
}
