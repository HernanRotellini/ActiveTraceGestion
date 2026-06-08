import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MainLayout from '@/layouts/MainLayout'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SessionProvider } from '@/shared/hooks/useSession'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

function renderWithProviders(initialEntries: string[]) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 }, mutations: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <MemoryRouter initialEntries={initialEntries}>
          <Routes>
            <Route path="*" element={<MainLayout />} />
          </Routes>
        </MemoryRouter>
      </SessionProvider>
    </QueryClientProvider>,
  )
}

describe('SidebarPermissions', () => {
  it('renders menu items', () => {
    renderWithProviders(['/'])
    expect(screen.getByText('Inicio')).toBeInTheDocument()
  })
})
