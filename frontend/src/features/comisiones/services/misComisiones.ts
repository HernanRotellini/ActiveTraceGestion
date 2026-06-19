import api from '@/shared/services/api'
import type { MisComisionesFilters, MisComisionesItem } from '@/features/comisiones/types/misComisiones'

export async function listarMisComisiones(filters?: MisComisionesFilters): Promise<MisComisionesItem[]> {
  const { data } = await api.get<MisComisionesItem[]>('/asignaciones/mis-comisiones', { params: filters })
  return data
}

export async function obtenerMiComision(id: string): Promise<MisComisionesItem> {
  const { data } = await api.get<MisComisionesItem>(`/asignaciones/mis-comisiones/${id}`)
  return data
}
