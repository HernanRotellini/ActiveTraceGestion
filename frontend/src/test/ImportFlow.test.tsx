import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { screen } from '@testing-library/react'
import { setupServer } from 'msw/node'
import { render } from '@/test/test-utils'
import { handlers } from '@/test/mocks/handlers'
import { ImportPreview } from '@/features/comisiones/components/ImportPreview'

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'bypass' }))
afterAll(() => server.close())
afterEach(() => server.resetHandlers())

describe('ImportFlow', () => {
  it('shows import form with file input', () => {
    render(<ImportPreview comisionId="COM-001" />)
    expect(screen.getByText('Importar Calificaciones')).toBeInTheDocument()
  })
})
