import api from '@/shared/services/api'
import type {
  Carrera,
  CarreraPayload,
  Cohorte,
  CohortePayload,
  Materia,
  MateriaPayload,
  UsuarioAdmin,
  UsuarioAdminPayload,
  UsuarioAdminFilters,
  MetricasDashboard,
  AuditoriaEntry,
  AuditoriaFilters,
} from '@/features/admin/types'

export async function listarCarreras() {
  const { data } = await api.get<{ items: Carrera[]; total: number }>('/estructura-academica/carreras')
  return data
}

export async function obtenerCarrera(id: string) {
  const { data } = await api.get<Carrera>(`/estructura-academica/carreras/${id}`)
  return data
}

export async function crearCarrera(payload: CarreraPayload) {
  const { data } = await api.post<Carrera>('/estructura-academica/carreras', payload)
  return data
}

export async function actualizarCarrera(id: string, payload: Partial<CarreraPayload>) {
  const { data } = await api.patch<Carrera>(`/estructura-academica/carreras/${id}`, payload)
  return data
}

export async function eliminarCarrera(id: string) {
  await api.delete(`/estructura-academica/carreras/${id}`)
}

export async function listarCohortes(carreraId?: string) {
  const { data } = await api.get<{ items: Cohorte[]; total: number }>('/estructura-academica/cohortes', {
    params: carreraId ? { carrera_id: carreraId } : undefined,
  })
  return data
}

export async function crearCohorte(payload: CohortePayload) {
  const { data } = await api.post<Cohorte>('/estructura-academica/cohortes', payload)
  return data
}

export async function actualizarCohorte(id: string, payload: Partial<CohortePayload>) {
  const { data } = await api.patch<Cohorte>(`/estructura-academica/cohortes/${id}`, payload)
  return data
}

export async function listarMaterias(carreraId?: string, cohorteId?: string) {
  const { data } = await api.get<{ items: Materia[]; total: number }>('/estructura-academica/materias', {
    params: { carrera_id: carreraId, cohorte_id: cohorteId },
  })
  return data
}

export async function crearMateria(payload: MateriaPayload) {
  const { data } = await api.post<Materia>('/estructura-academica/materias', payload)
  return data
}

export async function actualizarMateria(id: string, payload: Partial<MateriaPayload>) {
  const { data } = await api.patch<Materia>(`/estructura-academica/materias/${id}`, payload)
  return data
}

export async function listarUsuarios(filters?: UsuarioAdminFilters) {
  const { data } = await api.get<{ items: UsuarioAdmin[]; total: number }>('/usuarios', { params: filters })
  return data
}

export async function crearUsuario(payload: UsuarioAdminPayload) {
  const { data } = await api.post<UsuarioAdmin>('/usuarios', payload)
  return data
}

export async function actualizarUsuario(id: string, payload: Partial<UsuarioAdminPayload>) {
  const { data } = await api.patch<UsuarioAdmin>(`/usuarios/${id}`, payload)
  return data
}

export async function obtenerMetricas(filters?: { fecha_desde?: string; fecha_hasta?: string; materia?: string }) {
  const { data } = await api.get<MetricasDashboard>('/panel-auditoria/metricas', { params: filters })
  return data
}

export async function listarLogAuditoria(filters?: AuditoriaFilters) {
  const { data } = await api.get<{ items: AuditoriaEntry[]; total: number }>('/audit-trail', { params: filters })
  return data
}
