import { describe, expect, it, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import ColoquiosListPage from '@/features/coloquios/pages/ColoquiosListPage'
import EncuentrosListPage from '@/features/encuentros/pages/EncuentrosListPage'
import SetupCuatrimestrePage from '@/features/setup-cuatrimestre/pages/SetupCuatrimestrePage'

vi.mock('@/features/setup-cuatrimestre/hooks/usePeriodos', () => ({
  usePeriodosList: () => ({ data: { items: [] }, isLoading: false }),
  useProgramasList: () => ({ data: [], isLoading: false }),
  useFechasList: () => ({ data: [], isLoading: false }),
  useCrearPeriodo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActualizarPeriodoMutation: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActivarPeriodo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useDesactivarPeriodo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEliminarPeriodo: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useAgregarFechaMutation: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useQuitarFechaMutation: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useAgregarProgramaMutation: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useQuitarProgramaMutation: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearProgramaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActualizarProgramaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEliminarProgramaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCrearFechaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useActualizarFechaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEliminarFechaOficial: () => ({ mutateAsync: vi.fn(), isPending: false }),
}))

vi.mock('@/features/admin/hooks/useAdmin', () => ({
  useCarreras: () => ({ data: { items: [] }, isLoading: false }),
  useCohortesList: () => ({ data: { items: [] }, isLoading: false }),
  useMaterias: () => ({ data: { items: [] }, isLoading: false }),
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
  it('SetupCuatrimestrePage renders title and setup actions', () => {
    render(<SetupCuatrimestrePage />)
    expect(screen.getByRole('heading', { name: 'Setup de Cuatrimestre' })).toBeInTheDocument()
    expect(screen.getAllByText('Periodo Lectivo').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Programas Oficiales').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Fechas de Evaluacion').length).toBeGreaterThan(0)
  })
})
