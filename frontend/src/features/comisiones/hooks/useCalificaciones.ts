import { useQuery } from '@tanstack/react-query'
import { listarCalificaciones } from '@/features/comisiones/services/calificaciones'

export function useCalificaciones(comisionId: string) {
  return useQuery({
    queryKey: ['calificaciones', comisionId],
    queryFn: () => listarCalificaciones(comisionId),
    staleTime: 30_000,
  })
}
