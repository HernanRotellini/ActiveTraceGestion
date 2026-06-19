import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/admin/services/api'
import type {
  CarreraPayload,
  CarreraUpdatePayload,
  CohortePayload,
  CohorteUpdatePayload,
  MateriaPayload,
  MateriaUpdatePayload,
  UsuarioAdminPayload,
  UsuarioAdminFilters,
  AuditoriaFilters,
  CarreraFilters,
} from '@/features/admin/types'

export function useCarreras(filters?: CarreraFilters) {
  return useQuery({
    queryKey: ['carreras', filters],
    queryFn: () => api.listarCarreras(filters),
    staleTime: 30_000,
  })
}

export function useCrearCarrera() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CarreraPayload) => api.crearCarrera(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['carreras'] }),
  })
}

export function useActualizarCarrera() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & CarreraUpdatePayload) =>
      api.actualizarCarrera(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['carreras'] }),
  })
}

export function useEliminarCarrera() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarCarrera(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['carreras'] }),
  })
}

export function useCohortes(carreraId?: string) {
  return useQuery({
    queryKey: ['cohortes', carreraId],
    queryFn: () => api.listarCohortes(carreraId),
    enabled: !!carreraId,
    staleTime: 30_000,
  })
}

export function useCohortesList() {
  return useQuery({
    queryKey: ['cohortes'],
    queryFn: () => api.listarCohortes(),
    staleTime: 30_000,
  })
}

export function useCrearCohorte() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CohortePayload) => api.crearCohorte(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cohortes'] }),
  })
}

export function useActualizarCohorte() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & CohorteUpdatePayload) =>
      api.actualizarCohorte(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cohortes'] }),
  })
}

export function useEliminarCohorte() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarCohorte(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cohortes'] }),
  })
}

export function useMaterias(carreraId?: string, cohorteId?: string) {
  return useQuery({
    queryKey: ['materias', carreraId, cohorteId],
    queryFn: () => api.listarMaterias(carreraId, cohorteId),
    staleTime: 30_000,
  })
}

export function useCrearMateria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: MateriaPayload) => api.crearMateria(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['materias'] }),
  })
}

export function useActualizarMateria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & MateriaUpdatePayload) =>
      api.actualizarMateria(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['materias'] }),
  })
}

export function useEliminarMateria() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarMateria(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['materias'] }),
  })
}

export function useUsuarios(filters?: UsuarioAdminFilters) {
  return useQuery({
    queryKey: ['usuarios-admin', filters],
    queryFn: async () => {
      const items = await api.listarUsuarios(filters)
      return { items, total: items.length }
    },
    staleTime: 30_000,
  })
}

export function useCrearUsuario() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: UsuarioAdminPayload) => api.crearUsuario(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['usuarios-admin'] }),
  })
}

export function useActualizarUsuario() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & Partial<UsuarioAdminPayload>) =>
      api.actualizarUsuario(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['usuarios-admin'] }),
  })
}

export function useMetricas(filters?: { fecha_desde?: string; fecha_hasta?: string; materia?: string }) {
  return useQuery({
    queryKey: ['metricas-auditoria', filters],
    queryFn: () => api.obtenerMetricas(filters),
    staleTime: 30_000,
  })
}

export function useLogAuditoria(filters?: AuditoriaFilters) {
  return useQuery({
    queryKey: ['log-auditoria', filters],
    queryFn: () => api.listarLogAuditoria(filters),
    staleTime: 30_000,
  })
}
