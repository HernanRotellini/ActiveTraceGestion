import { useQuery } from '@tanstack/react-query'
import { obtenerAtrasados } from '@/features/comisiones/services/calificaciones'

export function useAtrasados(comisionId: string) {
  return useQuery({
    queryKey: ['atrasados', comisionId],
    queryFn: () => obtenerAtrasados(comisionId),
    staleTime: 30_000,
  })
}
