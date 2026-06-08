import { useMutation } from '@tanstack/react-query'
import { requestRecovery } from '@/features/auth/services/auth'
import { ApiError } from '@/shared/types/api'
import { useCallback } from 'react'

export function useRecovery() {
  const mutation = useMutation({
    mutationFn: (data: { tenant_code: string; email: string }) =>
      requestRecovery(data),
  })

  const handleRecovery = useCallback(
    (data: { tenant_code: string; email: string }) => {
      mutation.mutate(data)
    },
    [mutation],
  )

  return {
    submit: handleRecovery,
    isLoading: mutation.isPending,
    isSuccess: mutation.isSuccess,
    data: mutation.data,
    error: mutation.error instanceof ApiError ? mutation.error : null,
  }
}
