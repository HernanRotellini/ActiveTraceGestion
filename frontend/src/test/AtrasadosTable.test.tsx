import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { AtrasadosTable } from '@/features/comisiones/components/AtrasadosTable'
import type { AtrasadosResponse } from '@/features/comisiones/types/calificaciones'

const mockData: AtrasadosResponse = {
  total: 2,
  items: [
    { alumno_id: 'a-1', alumno_nombre: 'Juan Perez', materia: 'Matemática', atraso_dias: 20, ultima_actividad: '2026-04-15' },
    { alumno_id: 'a-2', alumno_nombre: 'Maria Gomez', materia: 'Lengua', atraso_dias: 5, ultima_actividad: null },
  ],
}

describe('AtrasadosTable', () => {
  it('renders data when provided', () => {
    render(<AtrasadosTable data={mockData} />)
    expect(screen.getByText('Juan Perez')).toBeInTheDocument()
    expect(screen.getByText('Maria Gomez')).toBeInTheDocument()
    expect(screen.getByText('20 días')).toBeInTheDocument()
    expect(screen.getByText('5 días')).toBeInTheDocument()
  })

  it('renders empty state when no data', () => {
    render(<AtrasadosTable />)
    expect(screen.getByText('No hay alumnos atrasados.')).toBeInTheDocument()
  })

  it('renders empty state when items array is empty', () => {
    render(<AtrasadosTable data={{ total: 0, items: [] }} />)
    expect(screen.getByText('No hay alumnos atrasados.')).toBeInTheDocument()
  })
})
