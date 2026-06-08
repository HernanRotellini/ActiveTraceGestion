import { useMutation } from '@tanstack/react-query'
import { enviarComunicacion } from '@/features/comunicaciones/services/comunicaciones'
import type { EnvioRequest } from '@/features/comunicaciones/types/comunicaciones'

export function useEnviar() {
  return useMutation({
    mutationFn: (data: EnvioRequest) => enviarComunicacion(data),
  })
}
