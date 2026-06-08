import { useMutation } from '@tanstack/react-query'
import { resetPassword } from '@/features/auth/services/auth'
import { ApiError } from '@/shared/types/api'
import { useCallback } from 'react'

export function useResetPassword() {
  const mutation = useMutation({
    mutationFn: (data: { token: string; new_password: string }) =>
      resetPassword(data),
  })

  const handleReset = useCallback(
    (data: { token: string; new_password: string }) => {
      mutation.mutate(data)
    },
    [mutation],
  )

  return {
    submit: handleReset,
    isLoading: mutation.isPending,
    isSuccess: mutation.isSuccess,
    error: mutation.error instanceof ApiError ? mutation.error : null,
  }
}
