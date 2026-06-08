import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import ResetPasswordPage from '@/features/auth/pages/ResetPasswordPage'
import { handlers } from '@/test/mocks/handlers'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('ResetPasswordPage', () => {
  it('shows error if no token provided', () => {
    render(<ResetPasswordPage />)

    expect(screen.getByText(/token de recuperación no proporcionado/i)).toBeInTheDocument()
  })

  it('renders reset form with token', () => {
    render(<ResetPasswordPage />, { initialEntries: ['/auth/restablecer?token=valid-token'] })

    expect(screen.getByLabelText('Nueva contraseña')).toBeInTheDocument()
    expect(screen.getByLabelText('Confirmar contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /restablecer contraseña/i })).toBeInTheDocument()
  })

  it('shows validation error for short password', async () => {
    const user = userEvent.setup()
    render(<ResetPasswordPage />, { initialEntries: ['/auth/restablecer?token=valid-token'] })

    await user.type(screen.getByLabelText('Nueva contraseña'), 'short')
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'short')
    await user.click(screen.getByRole('button', { name: /restablecer contraseña/i }))

    await waitFor(() => {
      expect(screen.getByText(/al menos 8 caracteres/i)).toBeInTheDocument()
    })
  })

  it('shows error for password mismatch', async () => {
    const user = userEvent.setup()
    render(<ResetPasswordPage />, { initialEntries: ['/auth/restablecer?token=valid-token'] })

    await user.type(screen.getByLabelText('Nueva contraseña'), 'password123')
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'different')
    await user.click(screen.getByRole('button', { name: /restablecer contraseña/i }))

    await waitFor(() => {
      expect(screen.getByText('Las contraseñas no coinciden')).toBeInTheDocument()
    })
  })

  it('redirects on expired token error', async () => {
    const user = userEvent.setup()
    render(<ResetPasswordPage />, { initialEntries: ['/auth/restablecer?token=expired-token'] })

    await user.type(screen.getByLabelText('Nueva contraseña'), 'newpassword123')
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'newpassword123')
    await user.click(screen.getByRole('button', { name: /restablecer contraseña/i }))

    await waitFor(() => {
      expect(screen.getByText(/token.*inválido.*expirado/i)).toBeInTheDocument()
    })
  })
})
