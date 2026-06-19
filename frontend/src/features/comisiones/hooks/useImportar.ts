import { useMutation, useQueryClient } from '@tanstack/react-query'
import { importarCalificaciones, confirmarImportacion } from '@/features/comisiones/services/calificaciones'

export function useImportar(materiaId: string, cohorteId: string) {
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (file: File) => importarCalificaciones(materiaId, cohorteId, file),
  })

  const confirmMutation = useMutation({
    mutationFn: ({ previewToken, actividadIds }: { previewToken: string; actividadIds: string[] }) =>
      confirmarImportacion(previewToken, actividadIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calificaciones', materiaId] })
    },
  })

  return {
    upload: uploadMutation,
    confirm: confirmMutation,
    isLoading: uploadMutation.isPending || confirmMutation.isPending,
  }
}
