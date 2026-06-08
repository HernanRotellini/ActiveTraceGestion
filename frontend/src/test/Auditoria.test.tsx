import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import AuditoriaDashboardPage from '@/features/admin/pages/AuditoriaDashboardPage'
import AuditoriaLogPage from '@/features/admin/pages/AuditoriaLogPage'
import { AuditoriaFiltros } from '@/features/admin/components/AuditoriaFiltros'

describe('AuditoriaDashboardPage', () => {
  it('renders title and filters', () => {
    render(<AuditoriaDashboardPage />)
    expect(screen.getByText('Panel de Auditoría')).toBeInTheDocument()
    expect(screen.getByText('Usuario')).toBeInTheDocument()
    expect(screen.getByText('Materia')).toBeInTheDocument()
  })
})

describe('AuditoriaLogPage', () => {
  it('renders title and filter fields', () => {
    render(<AuditoriaLogPage />)
    expect(screen.getByText('Log de Auditoría')).toBeInTheDocument()
    expect(screen.getByText('Acción')).toBeInTheDocument()
  })
})

describe('AuditoriaFiltros', () => {
  it('renders all filter inputs', () => {
    render(
      <AuditoriaFiltros
        onUsuarioChange={() => {}}
        onMateriaChange={() => {}}
        onAccionChange={() => {}}
        onFechaDesdeChange={() => {}}
        onFechaHastaChange={() => {}}
      />,
    )
    expect(screen.getByText('Usuario')).toBeInTheDocument()
    expect(screen.getByText('Materia')).toBeInTheDocument()
    expect(screen.getByText('Acción')).toBeInTheDocument()
    expect(screen.getByText('Desde')).toBeInTheDocument()
    expect(screen.getByText('Hasta')).toBeInTheDocument()
  })
})
