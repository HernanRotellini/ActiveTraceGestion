import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { obtenerUmbral, configurarUmbral } from '@/features/comisiones/services/calificaciones'
import type { UmbralConfig } from '@/features/comisiones/types/calificaciones'

export function useUmbral(materiaId: string, asignacionId: string) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['umbral', materiaId, asignacionId],
    queryFn: () => obtenerUmbral(materiaId, asignacionId),
    enabled: !!materiaId && !!asignacionId,
    staleTime: 30_000,
  })

  const mutation = useMutation({
    mutationFn: (data: Pick<UmbralConfig, 'umbral_pct' | 'valores_aprobatorios'>) =>
      configurarUmbral(materiaId, asignacionId, {
        umbral_pct: data.umbral_pct,
        valores_aprobatorios: data.valores_aprobatorios ?? [],
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['umbral', materiaId, asignacionId] })
    },
  })

  return { query, mutation }
}
