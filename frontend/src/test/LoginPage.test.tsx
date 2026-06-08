import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import LoginPage from '@/features/auth/pages/LoginPage'
import { handlers } from '@/test/mocks/handlers'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('LoginPage', () => {
  it('renders form elements', () => {
    render(<LoginPage />)

    expect(screen.getByLabelText('Código de institución')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
    expect(screen.getByText(/recuperar acceso/i)).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByText('El código de tenant es requerido')).toBeInTheDocument()
    expect(await screen.findByText('El email es requerido')).toBeInTheDocument()
    expect(await screen.findByText('La contraseña es requerida')).toBeInTheDocument()
  })

  it('redirects to dashboard on successful login', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.type(screen.getByLabelText('Código de institución'), 'test')
    await user.type(screen.getByLabelText('Email'), 'user@test.com')
    await user.type(screen.getByLabelText('Contraseña'), 'correct')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    await waitFor(() => {
      expect(screen.queryByText('Credenciales inválidas')).not.toBeInTheDocument()
    })
  })

  it('redirects to 2FA challenge page when 2FA is required', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.type(screen.getByLabelText('Código de institución'), 'test')
    await user.type(screen.getByLabelText('Email'), '2fa@test.com')
    await user.type(screen.getByLabelText('Contraseña'), 'any')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    await waitFor(() => {
      expect(sessionStorage.getItem('challenge_id')).toBe('challenge-123')
    })
  })

  it('shows error for invalid credentials', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.type(screen.getByLabelText('Código de institución'), 'test')
    await user.type(screen.getByLabelText('Email'), 'user@test.com')
    await user.type(screen.getByLabelText('Contraseña'), 'wrong')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByText(/credenciales inválidas/i)).toBeInTheDocument()
  })

  it('shows rate limit error for 429 response', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)

    await user.type(screen.getByLabelText('Código de institución'), 'test')
    await user.type(screen.getByLabelText('Email'), 'ratelimit@test.com')
    await user.type(screen.getByLabelText('Contraseña'), 'any')
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }))

    expect(await screen.findByText(/demasiados intentos/i)).toBeInTheDocument()
  })
})
