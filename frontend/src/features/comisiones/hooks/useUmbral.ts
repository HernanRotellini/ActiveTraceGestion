import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { obtenerUmbral, configurarUmbral } from '@/features/comisiones/services/calificaciones'
import type { UmbralConfig } from '@/features/comisiones/types/calificaciones'

export function useUmbral(comisionId: string) {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ['umbral', comisionId],
    queryFn: () => obtenerUmbral(comisionId),
    staleTime: 30_000,
  })

  const mutation = useMutation({
    mutationFn: (data: Partial<UmbralConfig>) => configurarUmbral(comisionId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['umbral', comisionId] })
    },
  })

  return { query, mutation }
}
