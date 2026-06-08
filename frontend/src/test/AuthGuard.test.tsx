import { describe, it, expect, afterEach } from 'vitest'
import { screen } from '@testing-library/react'
import { Routes, Route } from 'react-router-dom'
import { render } from '@/test/test-utils'
import { AuthGuard } from '@/guards/AuthGuard'
import { writeSession } from '@/shared/services/session'

describe('AuthGuard', () => {
  afterEach(() => {
    sessionStorage.clear()
  })

  it('redirects unauthenticated user to login', () => {
    render(
      <Routes>
        <Route element={<AuthGuard />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>,
      { initialEntries: ['/dashboard'] },
    )

    expect(screen.getByText('Login Page')).toBeInTheDocument()
  })

  it('allows authenticated user to access protected route', () => {
    writeSession({
      access_token: 'token',
      refresh_token: 'refresh',
      user: {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        roles: ['admin'],
      },
    })

    render(
      <Routes>
        <Route element={<AuthGuard />}>
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Route>
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>,
      { initialEntries: ['/dashboard'] },
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
