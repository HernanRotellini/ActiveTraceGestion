import { useQuery } from '@tanstack/react-query'
import { listarMisComisiones, obtenerMiComision } from '@/features/comisiones/services/misComisiones'
import type { MisComisionesFilters } from '@/features/comisiones/types/misComisiones'

export function useMisComisiones(filters?: MisComisionesFilters) {
  return useQuery({
    queryKey: ['mis-comisiones', filters],
    queryFn: () => listarMisComisiones(filters),
    staleTime: 30_000,
  })
}

export function useMiComision(id: string) {
  return useQuery({
    queryKey: ['mi-comision', id],
    queryFn: () => obtenerMiComision(id),
    enabled: !!id,
    staleTime: 30_000,
  })
}
