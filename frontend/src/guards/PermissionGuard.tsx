import { useSession } from '@/shared/hooks/useSession'
import ForbiddenPage from '@/pages/ForbiddenPage'

interface PermissionGuardProps {
  requiredPermissions?: string[]
  requireAll?: boolean
  children: React.ReactNode
}

export function PermissionGuard({
  requiredPermissions,
  requireAll = true,
  children,
}: PermissionGuardProps) {
  const { hasPermission } = useSession()

  if (!requiredPermissions || requiredPermissions.length === 0) {
    return <>{children}</>
  }

  const hasAccess = requireAll
    ? requiredPermissions.every((p) => hasPermission(p))
    : requiredPermissions.some((p) => hasPermission(p))

  if (!hasAccess) {
    return <ForbiddenPage />
  }

  return <>{children}</>
}
