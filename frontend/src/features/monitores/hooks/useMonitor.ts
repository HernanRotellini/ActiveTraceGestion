import { useQuery } from '@tanstack/react-query'
import { obtenerMonitor } from '@/features/monitores/services/monitores'
import type { MonitorFilters } from '@/features/monitores/types/monitores'

export function useMonitor(filters?: MonitorFilters) {
  return useQuery({
    queryKey: ['monitor', filters],
    queryFn: () => obtenerMonitor(filters),
    staleTime: 30_000,
  })
}
