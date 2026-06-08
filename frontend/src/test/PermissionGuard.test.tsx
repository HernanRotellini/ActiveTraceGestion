import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { PermissionGuard } from '@/guards/PermissionGuard'
import { writeSession } from '@/shared/services/session'

describe('PermissionGuard', () => {
  beforeEach(() => {
    writeSession({
      access_token: 'token',
      refresh_token: 'refresh',
      user: {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        roles: ['admin'],
        permissions: ['alumnos:ver', 'materias:ver'],
      },
    })
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  it('renders children when user has required permission', () => {
    render(
      <PermissionGuard requiredPermissions={['alumnos:ver']}>
        <div>Protected Content</div>
      </PermissionGuard>,
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('shows 403 when user lacks required permission', () => {
    render(
      <PermissionGuard requiredPermissions={['comunicaciones:ver']}>
        <div>Protected Content</div>
      </PermissionGuard>,
    )

    expect(screen.getByText('Acceso denegado')).toBeInTheDocument()
  })
})
