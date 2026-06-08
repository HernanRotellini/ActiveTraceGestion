import { useMutation } from '@tanstack/react-query'
import { generarPreview } from '@/features/comunicaciones/services/comunicaciones'
import type { PreviewRequest } from '@/features/comunicaciones/types/comunicaciones'

export function usePreview() {
  return useMutation({
    mutationFn: (data: PreviewRequest) => generarPreview(data),
  })
}
