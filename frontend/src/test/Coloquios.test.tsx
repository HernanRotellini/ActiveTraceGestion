import { describe, it, expect } from 'vitest'
import { render, screen } from './test-utils'

const ColoquiosListPage = () => <div data-testid="coloquios-list">Lista de Coloquios</div>
const ColoquioDetailPage = () => <div data-testid="coloquio-detail">Detalle de Coloquio</div>

describe('Coloquios pages', () => {
  it('renders ColoquiosListPage component', () => {
    render(<ColoquiosListPage />)
    expect(screen.getByTestId('coloquios-list')).toBeDefined()
  })

  it('renders ColoquioDetailPage component', () => {
    render(<ColoquioDetailPage />)
    expect(screen.getByTestId('coloquio-detail')).toBeDefined()
  })
})
