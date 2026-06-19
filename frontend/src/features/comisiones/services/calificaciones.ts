import api from '@/shared/services/api'
import type {
  CalificacionesResponse,
  ImportConfirmResponse,
  ImportPreviewResponse,
  RankingResponse,
  ReportesRapidosResponse,
  NotasFinalesResponse,
  UmbralConfig,
  AtrasadoItem,
} from '@/features/comisiones/types/calificaciones'

export async function importarCalificaciones(
  materiaId: string,
  cohorteId: string,
  file: File,
): Promise<ImportPreviewResponse> {
  const formData = new FormData()
  formData.append('archivo', file)
  const response = await api.post('/calificaciones/import/preview', formData, {
    params: { materia_id: materiaId, cohorte_id: cohorteId },
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function confirmarImportacion(
  previewToken: string,
  actividadIds: string[],
): Promise<ImportConfirmResponse> {
  const response = await api.post('/calificaciones/import/confirm', {
    preview_token: previewToken,
    actividad_ids: actividadIds,
  })
  return response.data
}

export async function listarCalificaciones(materiaId: string) {
  const response = await api.get<CalificacionesResponse>('/calificaciones', {
    params: { materia_id: materiaId },
  })
  return response.data
}

export async function configurarUmbral(
  materiaId: string,
  asignacionId: string,
  data: { umbral_pct: number; valores_aprobatorios: string[] },
): Promise<UmbralConfig> {
  const response = await api.put('/calificaciones/umbral', data, {
    params: { materia_id: materiaId, asignacion_id: asignacionId },
  })
  return response.data
}

export async function obtenerUmbral(materiaId: string, asignacionId: string): Promise<UmbralConfig> {
  const response = await api.get('/calificaciones/umbral', {
    params: { materia_id: materiaId, asignacion_id: asignacionId },
  })
  return response.data
}

export async function obtenerAtrasados(materiaId: string): Promise<AtrasadoItem[]> {
  const response = await api.get(`/analisis/atrasados/${materiaId}`)
  return response.data
}

export async function obtenerRanking(materiaId: string): Promise<RankingResponse> {
  const response = await api.get(`/analisis/ranking/${materiaId}`)
  return response.data
}

export async function obtenerNotasFinales(materiaId: string, actividades: string[]): Promise<NotasFinalesResponse> {
  const response = await api.get(`/analisis/notas-finales/${materiaId}`, {
    params: { actividades: actividades.join(',') },
  })
  return response.data
}

export async function obtenerReportesRapidos(materiaId: string): Promise<ReportesRapidosResponse> {
  const response = await api.get(`/analisis/reportes/${materiaId}`)
  return response.data
}
