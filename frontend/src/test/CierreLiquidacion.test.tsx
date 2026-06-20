import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { SessionProvider } from '@/shared/hooks/useSession'
import LiquidacionPeriodoPage from '@/features/liquidaciones/pages/LiquidacionPeriodoPage'
vi.mock('@/features/admin/hooks/useAdmin', () => ({
  useCohortesList: () => ({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
}))

vi.mock('@/features/liquidaciones/hooks/useLiquidaciones', () => ({
  usePreviewLiquidacion: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useCerrarLiquidacion: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}))

function renderWithProviders() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  })
  return (
    <QueryClientProvider client={qc}>
      <SessionProvider>
        <MemoryRouter initialEntries={['/liquidaciones']}>
          <LiquidacionPeriodoPage />
        </MemoryRouter>
      </SessionProvider>
    </QueryClientProvider>
  )
}

describe('LiquidacionPeriodoPage', () => {
  it('renders title', () => {
    const { container } = render(renderWithProviders())
    expect(container).toBeDefined()
  })
})
