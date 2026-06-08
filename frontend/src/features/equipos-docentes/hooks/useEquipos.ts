import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/equipos-docentes/services/api'
import type { EquiposFilters, AsignacionMasivaPayload, ClonePayload, VigenciaPayload } from '@/features/equipos-docentes/types'

export function useEquiposList(filters?: EquiposFilters) {
  return useQuery({
    queryKey: ['equipos-docentes', filters],
    queryFn: () => api.listarEquipos(filters),
    staleTime: 30_000,
  })
}

export function useEquipo(id: string) {
  return useQuery({
    queryKey: ['equipo', id],
    queryFn: () => api.obtenerEquipo(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { materia_id: string; carrera: string }) => api.crearEquipo(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['equipos-docentes'] }),
  })
}

export function useActualizarEquipo(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { materia_id?: string; carrera?: string; estado?: string }) => api.actualizarEquipo(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['equipos-docentes'] }); qc.invalidateQueries({ queryKey: ['equipo', id] }) },
  })
}

export function useEliminarEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarEquipo(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['equipos-docentes'] }),
  })
}

export function useAsignacionMasiva() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: AsignacionMasivaPayload) => api.asignacionMasiva(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['equipos-docentes'] }),
  })
}

export function useClonarEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ClonePayload) => api.clonarEquipo(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['equipos-docentes'] }),
  })
}

export function useActualizarVigencia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: VigenciaPayload }) => api.actualizarVigencia(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['equipos-docentes'] }),
  })
}
