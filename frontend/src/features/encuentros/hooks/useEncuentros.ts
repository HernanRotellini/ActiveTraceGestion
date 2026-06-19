import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/encuentros/services/api'
import type {
  SlotEncuentroPayload,
  InstanciaEncuentroPayload,
  InstanciaEncuentroUpdate,
  EncuentrosFilters,
  AdminInstanciasFilters,
} from '@/features/encuentros/types'

export function useSlotsList(filters?: EncuentrosFilters) {
  return useQuery({
    queryKey: ['encuentros-slots', filters],
    queryFn: () => api.listarSlots(filters),
    staleTime: 30_000,
  })
}

export function useInstanciasList(filters?: EncuentrosFilters) {
  return useQuery({
    queryKey: ['encuentros-instancias', filters],
    queryFn: () => api.listarInstancias(filters),
    staleTime: 30_000,
  })
}

export function useAdminInstancias(filters?: AdminInstanciasFilters) {
  return useQuery({
    queryKey: ['encuentros-admin', filters],
    queryFn: () => api.adminListarInstancias(filters),
    staleTime: 30_000,
  })
}

export function useCrearSlot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: SlotEncuentroPayload) => api.crearSlot(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['encuentros-slots'] })
      qc.invalidateQueries({ queryKey: ['encuentros-instancias'] })
      qc.invalidateQueries({ queryKey: ['encuentros-admin'] })
    },
  })
}

export function useCrearInstancia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: InstanciaEncuentroPayload) => api.crearInstancia(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['encuentros-instancias'] })
      qc.invalidateQueries({ queryKey: ['encuentros-admin'] })
    },
  })
}

export function useActualizarInstancia() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, update }: { id: string; update: InstanciaEncuentroUpdate }) =>
      api.actualizarInstancia(id, update),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['encuentros-instancias'] })
      qc.invalidateQueries({ queryKey: ['encuentros-admin'] })
    },
  })
}
