import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  aprobarLote,
  cancelarComunicacion,
  cancelarLote,
  enviarMasivo,
  generarPreview,
  listarLotes,
} from '@/features/comunicaciones/services/comunicaciones'

export function useComunicaciones() {
  const queryClient = useQueryClient()
  const invalidarLotes = () => queryClient.invalidateQueries({ queryKey: ['comunicaciones', 'lotes'] })

  const lotesQuery = useQuery({
    queryKey: ['comunicaciones', 'lotes'],
    queryFn: listarLotes,
    staleTime: 10_000,
    refetchInterval: 10_000,
  })

  const previewMutation = useMutation({ mutationFn: generarPreview })

  const enviarMutation = useMutation({
    mutationFn: enviarMasivo,
    onSuccess: invalidarLotes,
  })

  const aprobarMutation = useMutation({
    mutationFn: aprobarLote,
    onSuccess: invalidarLotes,
  })

  const cancelarLoteMutation = useMutation({
    mutationFn: cancelarLote,
    onSuccess: invalidarLotes,
  })

  const cancelarComunicacionMutation = useMutation({
    mutationFn: cancelarComunicacion,
    onSuccess: invalidarLotes,
  })

  return {
    lotesQuery,
    previewMutation,
    enviarMutation,
    aprobarMutation,
    cancelarLoteMutation,
    cancelarComunicacionMutation,
  }
}
