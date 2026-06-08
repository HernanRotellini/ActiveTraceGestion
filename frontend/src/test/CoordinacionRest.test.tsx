import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import EncuentrosListPage from '@/features/encuentros/pages/EncuentrosListPage'
import ColoquiosListPage from '@/features/coloquios/pages/ColoquiosListPage'
import SetupCuatrimestrePage from '@/features/setup-cuatrimestre/pages/SetupCuatrimestrePage'

vi.mock('@/features/setup-cuatrimestre/hooks/usePeriodos', () => ({
  usePeriodosList: () => ({ data: { items: [] }, isLoading: false }),
  useCrearPeriodo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActivarPeriodo: () => ({ mutate: vi.fn() }),
  useDesactivarPeriodo: () => ({ mutate: vi.fn() }),
}))

describe('Encuentros', () => {
  it('EncuentrosListPage renders list with filters', () => {
    render(<EncuentrosListPage />)
    expect(screen.getByText('Encuentros')).toBeInTheDocument()
    expect(screen.getByText('Fecha desde')).toBeInTheDocument()
    expect(screen.getByText('Fecha hasta')).toBeInTheDocument()
  })
})

describe('Coloquios', () => {
  it('ColoquiosListPage renders list with filters', () => {
    render(<ColoquiosListPage />)
    expect(screen.getByText('Coloquios')).toBeInTheDocument()
    expect(screen.getByText('Estado')).toBeInTheDocument()
  })
})

describe('SetupCuatrimestre', () => {
  it('SetupCuatrimestrePage renders title and new period button', () => {
    render(<SetupCuatrimestrePage />)
    expect(screen.getByText('Setup de Cuatrimestre')).toBeInTheDocument()
    expect(screen.getByText('Nuevo Período')).toBeInTheDocument()
  })
})
