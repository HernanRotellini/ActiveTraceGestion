import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import MonitorGeneralPage from '@/features/monitores/pages/MonitorGeneralPage'

describe('MonitorGeneral', () => {
  it('renders title and export button', () => {
    render(<MonitorGeneralPage />)
    expect(screen.getByText('Monitor General')).toBeInTheDocument()
    expect(screen.getByText('Exportar CSV')).toBeInTheDocument()
  })

  it('renders metric cards', () => {
    render(<MonitorGeneralPage />)
    expect(screen.getAllByText('Total Alumnos').length).toBeGreaterThan(0)
    expect(screen.getByText('Comisiones')).toBeInTheDocument()
    expect(screen.getByText('Promedio Atraso')).toBeInTheDocument()
    expect(screen.getByText('Entregas Pendientes')).toBeInTheDocument()
  })

  it('renders filters', () => {
    render(<MonitorGeneralPage />)
    expect(screen.getAllByText('Materia').length).toBeGreaterThan(0)
    expect(screen.getByText('Período')).toBeInTheDocument()
  })
})
