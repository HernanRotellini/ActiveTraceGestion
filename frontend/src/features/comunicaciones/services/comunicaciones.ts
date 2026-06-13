import api from '@/shared/services/api'
import type {
  PreviewRequest,
  PreviewResponse,
  EnvioRequest,
  EnvioResponse,
  MateriaOption,
  TrackingComunicacion,
} from '@/features/comunicaciones/types/comunicaciones'

export async function fetchMaterias(): Promise<MateriaOption[]> {
  const { data } = await api.get<MateriaOption[]>('/admin/materias')
  return data
}

export async function generarPreview(data: PreviewRequest): Promise<PreviewResponse> {
  const response = await api.post('/comunicaciones/preview', data)
  return response.data
}

export async function enviarComunicacion(data: EnvioRequest): Promise<EnvioResponse> {
  const response = await api.post('/comunicaciones/enviar', {
    materia_id: data.materia_id,
    asunto: data.asunto,
    cuerpo: data.cuerpo,
  })
  return response.data
}

export async function obtenerTracking(envioId: string): Promise<TrackingComunicacion> {
  const response = await api.get(`/comunicaciones/${envioId}/tracking`)
  return response.data
}
