import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/avisos/services/api'
import type { AvisoPayload, AvisosFilters } from '@/features/avisos/types'

export function useAvisosList(filters?: AvisosFilters) {
  return useQuery({
    queryKey: ['avisos-admin', filters],
    queryFn: () => api.listarAvisos(filters),
    staleTime: 30_000,
  })
}

export function useAviso(id: string) {
  return useQuery({
    queryKey: ['aviso', id],
    queryFn: () => api.obtenerAviso(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: AvisoPayload) => api.crearAviso(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}

export function useActualizarAviso(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<AvisoPayload>) => api.actualizarAviso(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['avisos'] }); qc.invalidateQueries({ queryKey: ['aviso', id] }) },
  })
}

export function usePublicarAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.publicarAviso(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}

export function useArchivarAviso() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.archivarAviso(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['avisos'] }),
  })
}
