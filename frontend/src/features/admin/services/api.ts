import api from '@/shared/services/api'
import type {
  Carrera,
  CarreraFilters,
  CarreraPayload,
  CarreraUpdatePayload,
  Cohorte,
  CohortePayload,
  CohorteUpdatePayload,
  Materia,
  MateriaPayload,
  MateriaUpdatePayload,
  UsuarioAdmin,
  UsuarioAdminPayload,
  UsuarioAdminFilters,
  AccionesPorDia,
  ComunicacionPorDocente,
  Interaccion,
  UltimaAccion,
  AuditoriaEntry,
  AuditoriaFilters,
} from '@/features/admin/types'

export async function listarCarreras(filters?: CarreraFilters) {
  const { data } = await api.get<{ items: Carrera[]; total: number }>('/admin/carreras', { params: filters })
  return data
}

export async function obtenerCarrera(id: string) {
  const { data } = await api.get<Carrera>(`/admin/carreras/${id}`)
  return data
}

export async function crearCarrera(payload: CarreraPayload) {
  const { data } = await api.post<Carrera>('/admin/carreras', payload)
  return data
}

export async function actualizarCarrera(id: string, payload: CarreraUpdatePayload) {
  const { data } = await api.patch<Carrera>(`/admin/carreras/${id}`, payload)
  return data
}

export async function eliminarCarrera(id: string) {
  await api.delete(`/admin/carreras/${id}`)
}

export async function listarCohortes(carreraId?: string) {
  const { data } = await api.get<{ items: Cohorte[]; total: number }>('/admin/cohortes', {
    params: carreraId ? { carrera_id: carreraId } : undefined,
  })
  return data
}

export async function crearCohorte(payload: CohortePayload) {
  const { data } = await api.post<Cohorte>('/admin/cohortes', payload)
  return data
}

export async function actualizarCohorte(id: string, payload: CohorteUpdatePayload) {
  const { data } = await api.patch<Cohorte>(`/admin/cohortes/${id}`, payload)
  return data
}

export async function eliminarCohorte(id: string) {
  await api.delete(`/admin/cohortes/${id}`)
}

export async function listarMaterias(carreraId?: string, cohorteId?: string) {
  const { data } = await api.get<{ items: Materia[]; total: number }>('/admin/materias', {
    params: { carrera_id: carreraId, cohorte_id: cohorteId },
  })
  return data
}

export async function crearMateria(payload: MateriaPayload) {
  const { data } = await api.post<Materia>('/admin/materias', payload)
  return data
}

export async function actualizarMateria(id: string, payload: MateriaUpdatePayload) {
  const { data } = await api.patch<Materia>(`/admin/materias/${id}`, payload)
  return data
}

export async function eliminarMateria(id: string) {
  await api.delete(`/admin/materias/${id}`)
}

export async function listarUsuarios(filters?: UsuarioAdminFilters) {
  const { data } = await api.get<UsuarioAdmin[]>('/admin/usuarios', { params: filters })
  return data
}

export async function crearUsuario(payload: UsuarioAdminPayload) {
  const { data } = await api.post<UsuarioAdmin>('/admin/usuarios', payload)
  return data
}

export async function actualizarUsuario(id: string, payload: Partial<UsuarioAdminPayload>) {
  const { data } = await api.patch<UsuarioAdmin>(`/admin/usuarios/${id}`, payload)
  return data
}

export async function listarAccionesPorDia(filters?: { fecha_desde?: string; fecha_hasta?: string; materia_id?: string }) {
  const { data } = await api.get<{ items: AccionesPorDia[] }>('/v1/auditoria/panel/acciones-por-dia', { params: filters })
  return data
}

export async function listarComunicacionesPorDocente(filters?: { fecha_desde?: string; fecha_hasta?: string; materia_id?: string }) {
  const { data } = await api.get<{ items: ComunicacionPorDocente[] }>('/v1/auditoria/panel/comunicaciones-por-docente', { params: filters })
  return data
}

export async function listarInteracciones(filters?: { fecha_desde?: string; fecha_hasta?: string; actor_id?: string }) {
  const { data } = await api.get<{ items: Interaccion[] }>('/v1/auditoria/panel/interacciones-por-docente-materia', { params: filters })
  return data
}

export async function listarUltimasAcciones(params?: { max_results?: number; offset?: number }) {
  const { data } = await api.get<{ items: UltimaAccion[] }>('/v1/auditoria/panel/ultimas-acciones', { params })
  return data
}

export async function listarLogAuditoria(filters?: AuditoriaFilters) {
  const { data } = await api.get<{ items: AuditoriaEntry[]; total: number }>('/v1/audit/logs', { params: filters })
  return data
}
