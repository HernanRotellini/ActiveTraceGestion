import { useQuery } from '@tanstack/react-query'
import { obtenerRanking } from '@/features/comisiones/services/calificaciones'

export function useRanking(materiaId: string) {
  return useQuery({
    queryKey: ['ranking', materiaId],
    queryFn: () => obtenerRanking(materiaId),
    enabled: !!materiaId,
    staleTime: 30_000,
  })
}
