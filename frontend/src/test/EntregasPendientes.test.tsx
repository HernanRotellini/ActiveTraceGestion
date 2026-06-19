import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen, waitFor, fireEvent } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import { handlers } from '@/test/mocks/handlers'
import EntregasPendientesPage from '@/features/entregas-sin-corregir/pages/EntregasPendientesPage'

const selectorHandlers = [
  http.get('/api/admin/carreras', () => HttpResponse.json({ items: [], total: 0 })),
  http.get('/api/admin/cohortes', () => HttpResponse.json({ items: [], total: 0 })),
  http.get('/api/admin/materias', () => HttpResponse.json({ items: [], total: 0 })),
]

const server = setupServer(...handlers, ...selectorHandlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('EntregasPendientesPage', () => {
  it('muestra el total de resultados y agrupa por actividad', async () => {
    render(<EntregasPendientesPage />)

    await waitFor(() => {
      expect(screen.getByText(/2 entregas pendientes en 2 actividades/i)).toBeInTheDocument()
    })
    // Las actividades funcionan como encabezado de grupo (eje principal).
    expect(screen.getByRole('heading', { name: /TP 1/ })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /TP 2/ })).toBeInTheDocument()
  })

  it('ofrece la carga del reporte LMS y el botón de exportación', () => {
    render(<EntregasPendientesPage />)

    expect(
      screen.getByRole('heading', { name: /Importar reporte LMS de finalización/i }),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Exportar entregas sin corregir/i })).toBeInTheDocument()
  })

  it('avisa con toast cuando se intenta procesar sin seleccionar materia', async () => {
    render(<EntregasPendientesPage />)

    fireEvent.click(screen.getByRole('button', { name: /Procesar reporte/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/Seleccioná carrera, cohorte y materia/i),
      ).toBeInTheDocument()
    })
  })
})
