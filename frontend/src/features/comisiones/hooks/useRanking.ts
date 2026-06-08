import { useQuery } from '@tanstack/react-query'
import { obtenerRanking } from '@/features/comisiones/services/calificaciones'

export function useRanking(comisionId: string) {
  return useQuery({
    queryKey: ['ranking', comisionId],
    queryFn: () => obtenerRanking(comisionId),
    staleTime: 30_000,
  })
}
