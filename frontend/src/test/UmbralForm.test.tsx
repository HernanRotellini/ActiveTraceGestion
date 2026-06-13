import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UmbralForm } from '@/features/comisiones/components/UmbralForm'

describe('UmbralForm', () => {
  it('renders the form with all inputs', () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
    })
    queryClient.setQueryData(['umbral', 'COM-001'], {
      nota_minima: 1,
      nota_maxima: 10,
      umbral_atraso: 5,
      umbral_promocion: 7,
    })
    render(
      <QueryClientProvider client={queryClient}>
        <UmbralForm comisionId="COM-001" />
      </QueryClientProvider>,
    )
    expect(screen.getByText('Configuración de Umbrales')).toBeInTheDocument()
    expect(screen.getByText('Nota mínima')).toBeInTheDocument()
    expect(screen.getByText('Nota máxima')).toBeInTheDocument()
    expect(screen.getByText('Umbral de atraso (días)')).toBeInTheDocument()
    expect(screen.getByText('Umbral de promoción')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /guardar configuración/i })).toBeInTheDocument()
  })
})
