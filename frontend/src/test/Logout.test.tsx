import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import { writeSession } from '@/shared/services/session'
import MainLayout from '@/layouts/MainLayout'
import { handlers } from '@/test/mocks/handlers'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionProvider } from '@/shared/hooks/useSession'
import type { ReactNode } from 'react'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => {
  server.resetHandlers()
  sessionStorage.clear()
})

describe('Logout', () => {
  it('clears session and redirects to login', async () => {
    writeSession({
      access_token: 'token',
      refresh_token: 'refresh-token-123',
      user: {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        roles: ['admin'],
      },
    })

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })

    function Wrapper({ children }: { children: ReactNode }) {
      return (
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={['/']}>
            <SessionProvider>{children}</SessionProvider>
          </MemoryRouter>
        </QueryClientProvider>
      )
    }

    const user = userEvent.setup()

    render(
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/login" element={<div>Login Page</div>} />
      </Routes>,
      { wrapper: Wrapper },
    )

    await user.click(screen.getByRole('button', { name: /cerrar sesión/i }))

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument()
    })

    expect(sessionStorage.getItem('trace_session')).toBeNull()
  })
})
