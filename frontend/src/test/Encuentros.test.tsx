import { describe, it, expect } from 'vitest'
import { render, screen } from './test-utils'

const EncuentrosListPage = () => <div data-testid="encuentros-list">Lista de Encuentros</div>
const EncuentroDetailPage = () => <div data-testid="encuentro-detail">Detalle de Encuentro</div>

describe('Encuentros pages', () => {
  it('renders EncuentrosListPage component', () => {
    render(<EncuentrosListPage />)
    expect(screen.getByTestId('encuentros-list')).toBeDefined()
    expect(screen.getByText('Lista de Encuentros')).toBeDefined()
  })

  it('renders EncuentroDetailPage component', () => {
    render(<EncuentroDetailPage />)
    expect(screen.getByTestId('encuentro-detail')).toBeDefined()
    expect(screen.getByText('Detalle de Encuentro')).toBeDefined()
  })
})
