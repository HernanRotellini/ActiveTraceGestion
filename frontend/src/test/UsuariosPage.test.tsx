import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import UsuariosPage from '@/features/admin/pages/UsuariosPage'
import { render } from '@/test/test-utils'

const server = setupServer(
  http.get('/api/admin/usuarios', () => HttpResponse.json([])),
)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('UsuariosPage', () => {
  it('explains that roles are managed in RBAC instead of this form', async () => {
    render(<UsuariosPage />)

    fireEvent.click(screen.getByRole('button', { name: 'Nuevo usuario' }))

    await waitFor(() => {
      expect(
        screen.getByText(/Los roles y permisos del usuario se administran desde el modulo RBAC/i),
      ).toBeInTheDocument()
    })

    expect(screen.queryByText('Roles')).not.toBeInTheDocument()
  })
})
