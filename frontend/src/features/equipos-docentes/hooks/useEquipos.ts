import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/equipos-docentes/services/api'
import type {
  CrearAsignacionesEquipoPayload,
  AsignacionListFilters,
  ClonePayload,
  VigenciaPayload,
} from '@/features/equipos-docentes/types'

export function useAsignacionesList(filters?: AsignacionListFilters) {
  return useQuery({
    queryKey: ['asignaciones-equipo', filters],
    queryFn: () => api.listarAsignaciones(filters),
    staleTime: 30_000,
  })
}

export function useCrearAsignacionesEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CrearAsignacionesEquipoPayload) => api.crearAsignacionesEquipo(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['asignaciones-equipo'] })
      qc.invalidateQueries({ queryKey: ['mis-comisiones'] })
    },
  })
}

export function useClonarEquipo() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ClonePayload) => api.clonarEquipo(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['asignaciones-equipo'] }),
  })
}

export function useActualizarVigencia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: VigenciaPayload) => api.actualizarVigencia(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['asignaciones-equipo'] }),
  })
}
