import { useQuery, useMutation } from '@tanstack/react-query'
import { detectarEntregas, exportarEntregas } from '@/features/entregas-sin-corregir/services/entregas'

export function useEntregasPendientes(comisionId?: string) {
  const query = useQuery({
    queryKey: ['entregasPendientes', comisionId],
    queryFn: () => detectarEntregas(comisionId),
    staleTime: 30_000,
  })

  const exportMutation = useMutation({
    mutationFn: () => exportarEntregas(comisionId),
  })

  return { query, exportMutation }
}
