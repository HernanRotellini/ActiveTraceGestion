import { useQuery } from '@tanstack/react-query'
import { listarCalificaciones } from '@/features/comisiones/services/calificaciones'

export function useCalificaciones(materiaId: string) {
  return useQuery({
    queryKey: ['calificaciones', materiaId],
    queryFn: () => listarCalificaciones(materiaId),
    enabled: !!materiaId,
    staleTime: 30_000,
  })
}
