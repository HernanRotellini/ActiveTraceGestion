import { useMutation } from '@tanstack/react-query'
import { logout as logoutApi } from '@/features/auth/services/auth'
import { useSession } from '@/shared/hooks/useSession'
import { useNavigate } from 'react-router-dom'
import { useCallback } from 'react'

export function useLogout() {
  const { session, logout: clearSession } = useSession()
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: () => logoutApi(session?.refresh_token ?? ''),
    onSettled: () => {
      clearSession()
      navigate('/login', { replace: true })
    },
  })

  const handleLogout = useCallback(() => {
    mutation.mutate()
  }, [mutation])

  return {
    logout: handleLogout,
    isLoading: mutation.isPending,
  }
}
