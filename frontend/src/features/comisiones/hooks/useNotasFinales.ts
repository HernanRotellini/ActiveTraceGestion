import { useQuery } from '@tanstack/react-query'
import { obtenerNotasFinales } from '@/features/comisiones/services/calificaciones'

export function useNotasFinales(comisionId: string) {
  return useQuery({
    queryKey: ['notasFinales', comisionId],
    queryFn: () => obtenerNotasFinales(comisionId),
    staleTime: 30_000,
  })
}
