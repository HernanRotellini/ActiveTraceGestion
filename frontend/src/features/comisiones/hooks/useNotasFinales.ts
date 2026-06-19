import { useQuery } from '@tanstack/react-query'
import { obtenerNotasFinales } from '@/features/comisiones/services/calificaciones'

export function useNotasFinales(materiaId: string, actividades: string[]) {
  return useQuery({
    queryKey: ['notasFinales', materiaId, actividades],
    queryFn: () => obtenerNotasFinales(materiaId, actividades),
    enabled: !!materiaId && actividades.length > 0,
    staleTime: 30_000,
  })
}
