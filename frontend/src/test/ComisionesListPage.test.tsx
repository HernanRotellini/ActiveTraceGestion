import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import ComisionesListPage from '@/features/comisiones/pages/ComisionesListPage'

describe('ComisionesListPage', () => {
  it('renders empty state when no comisiones', () => {
    render(<ComisionesListPage />)
    expect(screen.getByText('Mis Comisiones')).toBeInTheDocument()
    expect(screen.getByText('No hay comisiones asignadas.')).toBeInTheDocument()
  })
})
