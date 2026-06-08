import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import RecoveryPage from '@/features/auth/pages/RecoveryPage'
import { handlers } from '@/test/mocks/handlers'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('RecoveryPage', () => {
  it('renders recovery form', () => {
    render(<RecoveryPage />)

    expect(screen.getByLabelText('Código de institución')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /enviar instrucciones/i })).toBeInTheDocument()
  })

  it('shows success message after submission', async () => {
    const user = userEvent.setup()
    render(<RecoveryPage />)

    await user.type(screen.getByLabelText('Código de institución'), 'test')
    await user.type(screen.getByLabelText('Email'), 'user@test.com')
    await user.click(screen.getByRole('button', { name: /enviar instrucciones/i }))

    await waitFor(() => {
      expect(screen.getByText(/recibirá instrucciones/i)).toBeInTheDocument()
    })
  })
})
