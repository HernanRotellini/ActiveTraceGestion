import { describe, expect, it, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import SetupCuatrimestrePage from '@/features/setup-cuatrimestre/pages/SetupCuatrimestrePage'

vi.mock('@/features/setup-cuatrimestre/hooks/usePeriodos', () => ({
  usePeriodosList: () => ({ data: { items: [{ id: '1', nombre: '1C 2026', fecha_inicio: '2026-03-01', fecha_fin: '2026-07-15', activo: true, fechas: [], programas: [] }] }, isLoading: false }),
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

describe('SetupCuatrimestre page', () => {
  it('renders active period summary and section anchors', () => {
    render(<SetupCuatrimestrePage />)
    expect(screen.getByRole('heading', { name: 'Setup de Cuatrimestre' })).toBeInTheDocument()
    expect(screen.getAllByText('1C 2026').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Periodo Lectivo').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: 'Abrir Avisos' })).toBeInTheDocument()
  })
})
