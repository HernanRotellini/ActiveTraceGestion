import { describe, it, expect, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import MainLayout from '@/layouts/MainLayout'

const logoutSpy = vi.fn()

vi.mock('@/shared/hooks/useSession', () => ({
  useSession: () => ({
    session: {
      access_token: 'token',
      refresh_token: 'refresh',
      user: {
        user_id: 'user-1',
        tenant_id: 'tenant-1',
        email: 'ada@example.com',
        nombre: 'Ada',
        apellidos: 'Lovelace',
        roles: ['ADMIN'],
        permissions: [],
      },
    },
    hasPermission: () => true,
  }),
}))

vi.mock('@/features/auth/hooks/useLogout', () => ({
  useLogout: () => ({
    logout: logoutSpy,
    isLoading: false,
  }),
}))

function renderWithRouter(initialEntry = '/') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<div>Inicio</div>} />
          <Route path="coordinacion/equipos-docentes" element={<div>Equipos docentes</div>} />
          <Route path="liquidaciones" element={<div>Liquidaciones</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('SidebarPermissions', () => {
  it('renders menu items', () => {
    renderWithRouter()
    expect(screen.getAllByText('Inicio')[0]).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Educativo' })).toHaveAttribute('aria-expanded', 'true')
  })

  it('collapses one category without hiding the others', () => {
    renderWithRouter('/coordinacion/equipos-docentes')

    expect(screen.getByRole('link', { name: 'Equipos docentes' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Liquidaciones' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Educativo' }))

    expect(screen.getByRole('button', { name: 'Educativo' })).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByRole('link', { name: 'Equipos docentes' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Facturacion y salarios' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Liquidaciones' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Educativo' }))

    expect(screen.getByRole('link', { name: 'Equipos docentes' })).toBeInTheDocument()
  })
})
