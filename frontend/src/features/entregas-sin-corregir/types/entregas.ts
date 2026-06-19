export interface EntregaPendiente {
  entrega_id: string
  alumno_id: string
  alumno_nombre: string
  actividad: string
  materia: string
  comision: string
  fecha_entrega: string
  dias_pendiente: number
}

export interface EntregasPendientesResponse {
  items: EntregaPendiente[]
  total: number
}

export interface PosibleEntregaSinCorregir {
  alumno_nombre: string
  alumno_apellidos: string
  actividad: string
}

export interface CompletionReportResponse {
  materia_id: string
  cohorte_id: string
  posibles_entregas_sin_corregir: PosibleEntregaSinCorregir[]
}
