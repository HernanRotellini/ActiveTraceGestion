import { useQuery } from '@tanstack/react-query'
import { obtenerReportesRapidos } from '@/features/comisiones/services/calificaciones'

export function useReportesRapidos(materiaId: string) {
  return useQuery({
    queryKey: ['reportes-rapidos', materiaId],
    queryFn: () => obtenerReportesRapidos(materiaId),
    enabled: !!materiaId,
    staleTime: 30_000,
  })
}
