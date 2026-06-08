import { Navigate, useLocation, Outlet } from 'react-router-dom'
import { useSession } from '@/shared/hooks/useSession'

export function AuthGuard() {
  const { isAuthenticated } = useSession()
  const location = useLocation()

  if (!isAuthenticated) {
    const redirectTo = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?redirectTo=${redirectTo}`} replace />
  }

  return <Outlet />
}
