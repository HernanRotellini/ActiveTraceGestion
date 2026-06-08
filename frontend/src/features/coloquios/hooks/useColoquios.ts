import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/coloquios/services/api'
import type { ColoquioPayload, ColoquiosFilters, ResultadoColoquio } from '@/features/coloquios/types'

export function useColoquiosList(filters?: ColoquiosFilters) {
  return useQuery({
    queryKey: ['coloquios', filters],
    queryFn: () => api.listarColoquios(filters),
    staleTime: 30_000,
  })
}

export function useColoquio(id: string) {
  return useQuery({
    queryKey: ['coloquio', id],
    queryFn: () => api.obtenerColoquio(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCrearColoquio() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: ColoquioPayload) => api.crearColoquio(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['coloquios'] }),
  })
}

export function useActualizarColoquio(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<ColoquioPayload>) => api.actualizarColoquio(id, payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['coloquios'] }); qc.invalidateQueries({ queryKey: ['coloquio', id] }) },
  })
}

export function useConfirmarReserva() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ coloquioId, reservaId }: { coloquioId: string; reservaId: string }) => api.confirmarReserva(coloquioId, reservaId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['coloquios'] }),
  })
}

export function useCancelarReserva() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ coloquioId, reservaId }: { coloquioId: string; reservaId: string }) => api.cancelarReserva(coloquioId, reservaId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['coloquios'] }),
  })
}

export function useRegistrarResultado() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ coloquioId, reservaId, resultado, nota }: { coloquioId: string; reservaId: string; resultado: ResultadoColoquio; nota?: number }) =>
      api.registrarResultado(coloquioId, reservaId, resultado, nota),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['coloquios'] }),
  })
}
