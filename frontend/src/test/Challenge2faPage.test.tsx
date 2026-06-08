import { describe, it, expect, beforeAll, afterAll, afterEach, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import Challenge2faPage from '@/features/auth/pages/Challenge2faPage'
import { handlers } from '@/test/mocks/handlers'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => {
  server.resetHandlers()
  sessionStorage.clear()
})

describe('Challenge2faPage', () => {
  beforeEach(() => {
    sessionStorage.setItem('challenge_id', 'challenge-123')
  })

  it('renders TOTP input form', () => {
    render(<Challenge2faPage />)

    expect(screen.getByLabelText('Código TOTP')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /verificar/i })).toBeInTheDocument()
  })

  it('validates 6-digit TOTP code', async () => {
    const user = userEvent.setup()
    render(<Challenge2faPage />)

    const input = screen.getByLabelText('Código TOTP')
    await user.type(input, '123456')

    expect(input).toHaveValue('123456')
  })

  it('redirects to login if no challenge_id', () => {
    sessionStorage.clear()
    render(<Challenge2faPage />)

    waitFor(() => {
      expect(window.location.pathname).toBe('/login')
    })
  })
})
