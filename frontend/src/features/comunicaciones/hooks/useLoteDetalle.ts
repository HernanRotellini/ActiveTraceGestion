import { useQuery } from '@tanstack/react-query'
import { detalleLote } from '@/features/comunicaciones/services/comunicaciones'

export function useLoteDetalle(loteId: string | null) {
  return useQuery({
    queryKey: ['comunicaciones', 'lote', loteId],
    queryFn: () => detalleLote(loteId!),
    enabled: !!loteId,
    refetchInterval: 8_000,
    staleTime: 5_000,
  })
}
