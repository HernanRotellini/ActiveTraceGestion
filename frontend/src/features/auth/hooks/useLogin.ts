import { useMutation } from '@tanstack/react-query'
import { login as loginApi } from '@/features/auth/services/auth'
import { getMe } from '@/features/auth/services/auth'
import { useSession } from '@/shared/hooks/useSession'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '@/shared/types/api'
import { useCallback } from 'react'

interface AccessTokenClaims {
  user_id: string
  tenant_id: string
  roles: string[]
  email?: string
}

function decodeAccessTokenClaims(accessToken: string): AccessTokenClaims {
  const [, payload] = accessToken.split('.')
  if (!payload) {
    throw new ApiError('Token de acceso inválido', 401, 'invalid_token')
  }

  const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/')
  const claims = JSON.parse(atob(normalizedPayload)) as AccessTokenClaims
  return claims
}

export function useLogin() {
  const { login: setSession } = useSession()
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: loginApi,
    onSuccess: async (data) => {
      if (data.requires_2fa && data.challenge_id) {
        sessionStorage.setItem('challenge_id', data.challenge_id)
        navigate('/auth/2fa', { replace: true })
        return
      }

      const claims = decodeAccessTokenClaims(data.access_token)
      const initialEmail = claims.email ?? null
      setSession(data.access_token, data.refresh_token, {
        user_id: claims.user_id,
        tenant_id: claims.tenant_id,
        roles: claims.roles,
        email: initialEmail,
      })

      const me = await getMe()
      setSession(data.access_token, data.refresh_token, {
        user_id: me.user_id,
        tenant_id: me.tenant_id,
        roles: me.roles,
        email: me.email ?? initialEmail,
      })

      const redirectTo = sessionStorage.getItem('redirectTo') ?? '/'
      sessionStorage.removeItem('redirectTo')
      navigate(redirectTo, { replace: true })
    },
  })

  const handleLogin = useCallback(
    (data: { tenant_code: string; email: string; password: string }) => {
      mutation.mutate(data)
    },
    [mutation],
  )

  return {
    login: handleLogin,
    isLoading: mutation.isPending,
    error: mutation.error instanceof ApiError ? mutation.error : null,
  }
}
