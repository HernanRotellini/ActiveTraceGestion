import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as api from '@/features/liquidaciones/services/api'
import type {
  LiquidacionFilters,
  LiquidacionPreviewRequest,
  LiquidacionCloseRequest,
  SalarioBaseCreate,
  SalarioBaseUpdate,
  SalarioPlusCreate,
  MateriaPlusCreate,
  FacturaCreate,
  FacturaUpdate,
  FacturaFilters,
} from '@/features/liquidaciones/types'

export function useSalariosBase() {
  return useQuery({
    queryKey: ['salarios-base'],
    queryFn: () => api.listarSalariosBase(),
    staleTime: 30_000,
  })
}

export function useCrearSalarioBase() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: SalarioBaseCreate) => api.crearSalarioBase(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }),
  })
}

export function useActualizarSalarioBase() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & SalarioBaseUpdate) =>
      api.actualizarSalarioBase(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['salarios-base'] }),
  })
}

export function useEliminarSalarioBase() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarSalarioBase(id),
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
    mutationFn: (payload: SalarioPlusCreate) => api.crearPlus(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['plus'] }),
  })
}

export function useMateriaPlus() {
  return useQuery({
    queryKey: ['materia-plus'],
    queryFn: () => api.listarMateriaPlus(),
    staleTime: 30_000,
  })
}

export function useCrearMateriaPlus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: MateriaPlusCreate) => api.crearMateriaPlus(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['materia-plus'] }),
  })
}

export function usePreviewLiquidacion() {
  return useMutation({
    mutationFn: (payload: LiquidacionPreviewRequest) => api.previewLiquidacion(payload),
  })
}

export function useCerrarLiquidacion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: LiquidacionCloseRequest) => api.cerrarLiquidacion(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['liquidaciones'] })
    },
  })
}

export function useLiquidaciones(filters?: LiquidacionFilters) {
  return useQuery({
    queryKey: ['liquidaciones', filters],
    queryFn: () => api.listarLiquidaciones(filters),
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
    mutationFn: (payload: FacturaCreate) => api.crearFactura(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}

export function useActualizarFactura() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...payload }: { id: string } & FacturaUpdate) =>
      api.actualizarFactura(id, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}

export function useEliminarFactura() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.eliminarFactura(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}

export function useMarcarAbonada() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.marcarFacturaAbonada(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['facturas'] }),
  })
}
