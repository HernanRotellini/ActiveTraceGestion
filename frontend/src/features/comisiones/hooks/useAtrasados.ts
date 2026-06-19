import { useQuery } from '@tanstack/react-query'
import { obtenerAtrasados } from '@/features/comisiones/services/calificaciones'

export function useAtrasados(materiaId: string) {
  return useQuery({
    queryKey: ['atrasados', materiaId],
    queryFn: () => obtenerAtrasados(materiaId),
    enabled: !!materiaId,
    staleTime: 30_000,
  })
}
