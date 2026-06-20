import { describe, expect, it, vi } from 'vitest'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import LiquidacionHistorialPage from '@/features/liquidaciones/pages/LiquidacionHistorialPage'
import LiquidacionPeriodoPage from '@/features/liquidaciones/pages/LiquidacionPeriodoPage'
import { render } from '@/test/test-utils'

const previewMutateAsync = vi.fn()
const cerrarMutateAsync = vi.fn()
const useLiquidacionesSpy = vi.fn(() => ({ data: [], isLoading: false }))

vi.mock('@/shared/hooks/useSession', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/shared/hooks/useSession')>()
  return {
    ...actual,
    useSession: () => ({
      hasPermission: () => true,
    }),
  }
})

vi.mock('@/features/admin/hooks/useAdmin', () => ({
  useCohortesList: () => ({
    data: {
      items: [
        {
          id: 'coh-1',
          carrera_id: 'car-1',
          nombre: 'Cohorte Marzo',
          anio: 2026,
          vig_desde: '2026-03-01',
          vig_hasta: null,
          estado: 'activa',
          activo: true,
          creada_en: '2026-01-01T00:00:00Z',
        },
      ],
      total: 1,
    },
    isLoading: false,
  }),
}))

vi.mock('@/features/liquidaciones/hooks/useLiquidaciones', () => ({
  usePreviewLiquidacion: () => ({
    mutateAsync: previewMutateAsync,
    isPending: false,
  }),
  useCerrarLiquidacion: () => ({
    mutateAsync: cerrarMutateAsync,
    isPending: false,
  }),
  useLiquidaciones: (filters?: unknown) => useLiquidacionesSpy(filters),
}))

describe('Liquidaciones pages', () => {
  it('submits liquidacion preview using a searchable cohorte selector', async () => {
    previewMutateAsync.mockReset()
    previewMutateAsync.mockResolvedValue({
      cohorte_id: 'coh-1',
      periodo: '2026-06',
      items: [],
      total_pagable: '0',
      segmento_nexo_total: '0',
      segmento_facturantes_total: '0',
    })

    render(<LiquidacionPeriodoPage />)

    const cohorteInput = screen.getByPlaceholderText('Seleccionar cohorte')
    fireEvent.focus(cohorteInput)
    fireEvent.click(screen.getByText('Cohorte Marzo (2026)'))
    fireEvent.change(screen.getByPlaceholderText('ej: 2026-06'), { target: { value: '2026-06' } })
    fireEvent.click(screen.getByRole('button', { name: 'Generar preview' }))

    await waitFor(() => {
      expect(previewMutateAsync).toHaveBeenCalledWith({
        cohorte_id: 'coh-1',
        periodo: '2026-06',
      })
    })
  })

  it('renders the historial filter with a cohorte combobox', async () => {
    useLiquidacionesSpy.mockClear()

    render(<LiquidacionHistorialPage />)

    const cohorteInput = screen.getByPlaceholderText('Todas las cohortes')
    fireEvent.focus(cohorteInput)
    fireEvent.click(screen.getByText('Cohorte Marzo (2026)'))

    await waitFor(() => {
      expect(useLiquidacionesSpy).toHaveBeenLastCalledWith({
        cohorte_id: 'coh-1',
      })
    })
  })
})
