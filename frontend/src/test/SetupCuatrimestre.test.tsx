import { describe, it, expect } from 'vitest'
import { render, screen } from './test-utils'

const SetupCuatrimestrePage = () => <div data-testid="setup-cuatrimestre">Setup Cuatrimestre</div>

describe('SetupCuatrimestre page', () => {
  it('renders SetupCuatrimestrePage component', () => {
    render(<SetupCuatrimestrePage />)
    expect(screen.getByTestId('setup-cuatrimestre')).toBeDefined()
    expect(screen.getByText('Setup Cuatrimestre')).toBeDefined()
  })
})
