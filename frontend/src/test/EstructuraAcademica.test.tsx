import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import CarrerasPage from '@/features/admin/pages/CarrerasPage'
import CohortesPage from '@/features/admin/pages/CohortesPage'
import MateriasPage from '@/features/admin/pages/MateriasPage'

describe('CarrerasPage', () => {
  it('renders title and new button', () => {
    render(<CarrerasPage />)
    expect(screen.getByText('Carreras')).toBeInTheDocument()
    expect(screen.getByText('Nueva carrera')).toBeInTheDocument()
  })
})

describe('CohortesPage', () => {
  it('renders title and carrera selector', () => {
    render(<CohortesPage />)
    expect(screen.getByText('Cohortes')).toBeInTheDocument()
    expect(screen.getByText('Carrera *')).toBeInTheDocument()
  })
})

describe('MateriasPage', () => {
  it('renders title and filters', () => {
    render(<MateriasPage />)
    expect(screen.getByText('Materias')).toBeInTheDocument()
    expect(screen.getByText('Carrera')).toBeInTheDocument()
    expect(screen.getByText('Cohorte')).toBeInTheDocument()
  })
})
