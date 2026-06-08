import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { PermissionGuard } from '@/guards/PermissionGuard'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionProvider } from '@/shared/hooks/useSession'
import { writeSession } from '@/shared/services/session'

beforeEach(() => {
  writeSession({
    access_token: 'test-token',
    refresh_token: 'test-refresh',
    user: {
      user_id: 'user-1',
      tenant_id: 'tenant-1',
      roles: ['admin'],
      permissions: ['calificaciones:ver', 'usuarios:ver'],
    },
  })
})

afterEach(() => {
  sessionStorage.clear()
})

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        {ui}
      </SessionProvider>
    </QueryClientProvider>,
  )
}

describe('RouteGuard', () => {
  it('renders ForbiddenPage when missing permission', () => {
    renderWithProviders(
      <PermissionGuard requiredPermissions={['inexistente:permiso']}>
        <div>Protected content</div>
      </PermissionGuard>,
    )
    expect(screen.getByText('403')).toBeInTheDocument()
    expect(screen.getByText('Acceso denegado')).toBeInTheDocument()
    expect(screen.queryByText('Protected content')).not.toBeInTheDocument()
  })

  it('renders children when permission is present', () => {
    renderWithProviders(
      <PermissionGuard requiredPermissions={['calificaciones:ver']}>
        <div>Protected content</div>
      </PermissionGuard>,
    )
    expect(screen.getByText('Protected content')).toBeInTheDocument()
    expect(screen.queryByText('403')).not.toBeInTheDocument()
  })
})
