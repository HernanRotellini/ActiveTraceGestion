import { useMutation, useQueryClient } from '@tanstack/react-query'
import { importarCalificaciones, confirmarImportacion } from '@/features/comisiones/services/calificaciones'

export function useImportar(comisionId: string) {
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (file: File) => importarCalificaciones(comisionId, file),
  })

  const confirmMutation = useMutation({
    mutationFn: (actividadIds: string[]) => confirmarImportacion(comisionId, actividadIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calificaciones', comisionId] })
    },
  })

  return {
    upload: uploadMutation,
    confirm: confirmMutation,
    isLoading: uploadMutation.isPending || confirmMutation.isPending,
  }
}
