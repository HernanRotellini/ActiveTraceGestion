import { useQuery } from '@tanstack/react-query'
import { obtenerTracking } from '@/features/comunicaciones/services/comunicaciones'

export function useTracking(envioId: string | null) {
  return useQuery({
    queryKey: ['tracking', envioId],
    queryFn: () => obtenerTracking(envioId!),
    enabled: !!envioId,
    refetchInterval: 5_000,
    staleTime: 4_000,
  })
}
