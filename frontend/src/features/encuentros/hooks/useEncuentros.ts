import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/encuentros/services/api'
import type { EncuentroPayload, EncuentrosFilters } from '@/features/encuentros/types'

export function useEncuentrosList(filters?: EncuentrosFilters) {
  return useQuery({
    queryKey: ['encuentros', filters],
    queryFn: () => api.listarEncuentros(filters),
    staleTime: 30_000,
  })
}

export function useEncuentro(id: string) {
  return useQuery({
    queryKey: ['encuentro', id],
    queryFn: () => api.obtenerEncuentro(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearEncuentro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: EncuentroPayload) => api.crearEncuentro(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['encuentros'] }),
  })
}

export function useActualizarEncuentro(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<EncuentroPayload>) => api.actualizarEncuentro(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['encuentros'] }); qc.invalidateQueries({ queryKey: ['encuentro', id] }) },
  })
}

export function useEliminarEncuentro() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarEncuentro(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['encuentros'] }),
  })
}

export function useAgregarGuardia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ encuentroId, payload }: { encuentroId: string; payload: { docente_id: string; hora_inicio: string; hora_fin: string } }) =>
      api.agregarGuardia(encuentroId, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['encuentros'] }),
  })
}

export function useQuitarGuardia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ encuentroId, guardiaId }: { encuentroId: string; guardiaId: string }) => api.quitarGuardia(encuentroId, guardiaId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['encuentros'] }),
  })
}
