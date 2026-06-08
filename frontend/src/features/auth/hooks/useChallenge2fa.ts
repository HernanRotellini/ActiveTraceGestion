import { useMutation } from '@tanstack/react-query'
import { challenge2fa as challenge2faApi, getMe } from '@/features/auth/services/auth'
import { useSession } from '@/shared/hooks/useSession'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '@/shared/types/api'
import { useCallback } from 'react'

export function useChallenge2fa() {
  const { login: setSession } = useSession()
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: (code: string) => {
      const challenge_id = sessionStorage.getItem('challenge_id')
      if (!challenge_id) {
        throw new ApiError('No hay desafío activo', 400, 'no_challenge')
      }
      return challenge2faApi({ challenge_id, code })
    },
    onSuccess: async (data) => {
      sessionStorage.removeItem('challenge_id')

      const me = await getMe()
      setSession(data.access_token, data.refresh_token, {
        user_id: me.user_id,
        tenant_id: me.tenant_id,
        roles: me.roles,
      })

      const redirectTo = sessionStorage.getItem('redirectTo') ?? '/'
      sessionStorage.removeItem('redirectTo')
      navigate(redirectTo, { replace: true })
    },
  })

  const handleChallenge = useCallback(
    (code: string) => {
      mutation.mutate(code)
    },
    [mutation],
  )

  return {
    submit: handleChallenge,
    isLoading: mutation.isPending,
    error: mutation.error instanceof ApiError ? mutation.error : null,
  }
}
