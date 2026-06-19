import { useQuery, useMutation } from '@tanstack/react-query'
import { detectarEntregas, exportarEntregas } from '@/features/entregas-sin-corregir/services/entregas'

export function useEntregasPendientes(comision?: string) {
  const query = useQuery({
    queryKey: ['entregasPendientes', comision],
    queryFn: () => detectarEntregas(comision),
    staleTime: 30_000,
  })

  const exportMutation = useMutation({
    mutationFn: () => exportarEntregas(comision),
  })

  return { query, exportMutation }
}
