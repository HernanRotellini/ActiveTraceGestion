import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import { handlers } from '@/test/mocks/handlers'
import ComunicacionesPage from '@/features/comunicaciones/pages/ComunicacionesPage'

const extraHandlers = [
  http.get('/api/admin/materias', () =>
    HttpResponse.json({
      items: [{ id: '00000000-0000-0000-0000-000000000001', nombre: 'Matemática', codigo: 'MAT' }],
      total: 1,
    }),
  ),
]

const server = setupServer(...handlers, ...extraHandlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('ComunicacionesPage', () => {
  it('muestra el formulario de composición y el panel de lotes', async () => {
    render(<ComunicacionesPage />)

    expect(screen.getByRole('heading', { name: 'Comunicaciones' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Nueva comunicación/i })).toBeInTheDocument()

    // El panel de lotes carga el lote mockeado con sus totales por estado.
    await waitFor(() => {
      expect(screen.getByText('Matemática')).toBeInTheDocument()
    })
    expect(screen.getByText(/Pend\.: 2/)).toBeInTheDocument()
    expect(screen.getByText(/2 destinatarios/)).toBeInTheDocument()
  })

  it('oculta las acciones de aprobación sin el permiso comunicacion:aprobar', async () => {
    render(<ComunicacionesPage />)

    await waitFor(() => {
      expect(screen.getByText('Matemática')).toBeInTheDocument()
    })
    expect(screen.queryByRole('button', { name: 'Aprobar' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Ver detalle/i })).toBeInTheDocument()
  })

  it('muestra las variables de plantilla soportadas en el formulario', () => {
    render(<ComunicacionesPage />)
    expect(screen.getByText('{{nombre}}')).toBeInTheDocument()
    expect(screen.getByText('{{materia}}')).toBeInTheDocument()
  })
})
