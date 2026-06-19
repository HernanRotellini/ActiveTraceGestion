import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import { DocenteSelector } from '@/features/equipos-docentes/components/DocenteSelector'
import { render } from '@/test/test-utils'

const mutateAsync = vi.fn(async (payload: { nombre: string; apellidos: string; email: string }) => ({
  id: 'docente-creado',
  nombre: payload.nombre,
  apellidos: payload.apellidos,
  email: payload.email,
  estado: 'activo',
  facturador: false,
  created_at: '2026-06-19T00:00:00Z',
  updated_at: '2026-06-19T00:00:00Z',
}))

vi.mock('@/features/admin/hooks/useAdmin', () => ({
  useUsuarios: () => ({
    data: {
      items: [
        {
          id: 'docente-existente',
          nombre: 'Mario',
          apellidos: 'Lopez',
          email: 'mario@test.com',
          estado: 'activo',
          facturador: false,
          created_at: '2026-06-19T00:00:00Z',
          updated_at: '2026-06-19T00:00:00Z',
        },
      ],
      total: 1,
    },
    isLoading: false,
  }),
  useCrearUsuario: () => ({
    isPending: false,
    mutateAsync,
  }),
}))

function Harness() {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  return <DocenteSelector selectedIds={selectedIds} onChange={setSelectedIds} />
}

describe('DocenteSelector', () => {
  it('shows quick-create first and adds the created docente to the selection', async () => {
    mutateAsync.mockClear()
    render(<Harness />)

    const input = screen.getByPlaceholderText('Buscar docente...')
    fireEvent.focus(input)

    await waitFor(() => {
      const options = screen.getAllByRole('option')
      expect(options[0]).toHaveTextContent('Crear nuevo docente')
    })

    fireEvent.click(screen.getByText('+ Crear nuevo docente'))

    fireEvent.change(screen.getByLabelText('Nombre *'), { target: { value: 'Ana' } })
    fireEvent.change(screen.getByLabelText('Apellidos *'), { target: { value: 'Perez' } })
    fireEvent.change(screen.getByLabelText('Email *'), { target: { value: 'ana@test.com' } })
    fireEvent.click(screen.getByRole('button', { name: 'Crear docente' }))

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith({
        nombre: 'Ana',
        apellidos: 'Perez',
        email: 'ana@test.com',
      })
      expect(screen.getByText('Ana Perez')).toBeInTheDocument()
      expect(screen.getByText('ana@test.com')).toBeInTheDocument()
    })
  })
})
