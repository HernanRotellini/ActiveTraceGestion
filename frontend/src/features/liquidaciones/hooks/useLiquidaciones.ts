import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/liquidaciones/services/api'
import type { LiquidacionFilters, SalarioBasePayload, PlusPayload, FacturaPayload, FacturaFilters } from '@/features/liquidaciones/types'

export function useLiquidacionActiva(filters?: LiquidacionFilters) {
  return useQuery({
    queryKey: ['liquidacion-activa', filters],
    queryFn: () => api.obtenerLiquidacionActiva(filters),
    staleTime: 30_000,
  })
}

export function useLiquidacion(id: string) {
  return useQuery({
    queryKey: ['liquidacion', id],
    queryFn: () => api.obtenerLiquidacion(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}

export function useCerrarLiquidacion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.cerrarLiquidacion(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['liquidacion-activa'] })
      qc.invalidateQueries({ queryKey: ['liquidacion'] })
      qc.invalidateQueries({ queryKey: ['historial-liquidaciones'] })
    },
  })
}

export function useHistorial(filters?: LiquidacionFilters) {
  return useQuery({
    queryKey: ['historial-liquidaciones', filters],
    queryFn: () => api.listarHistorial(filters),
    staleTime: 30_000,
  })
}

export function useGrillaSalarial() {
  return useQuery({
    queryKey: ['salarios-base'],
    queryFn: () => api.listarSalariosBase(),
    staleTime: 30_000,
  })
}

export function useCrearSalarioBase() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: SalarioBasePayload) => api.crearSalarioBase(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }),
  })
}

export function useActualizarSalarioBase(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<SalarioBasePayload>) => api.actualizarSalarioBase(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }),
  })
}

export function usePlus() {
  return useQuery({
    queryKey: ['plus'],
    queryFn: () => api.listarPlus(),
    staleTime: 30_000,
  })
}

export function useCrearPlus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: PlusPayload) => api.crearPlus(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plus'] }),
  })
}

export function useActualizarPlus(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: Partial<PlusPayload>) => api.actualizarPlus(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plus'] }),
  })
}

export function useFacturas(filters?: FacturaFilters) {
  return useQuery({
    queryKey: ['facturas', filters],
    queryFn: () => api.listarFacturas(filters),
    staleTime: 30_000,
  })
}

export function useCrearFactura() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: FacturaPayload) => api.crearFactura(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}

export function useCambiarEstadoFactura() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, estado }: { id: string; estado: 'pendiente' | 'abonada' }) => api.cambiarEstadoFactura(id, estado),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}
