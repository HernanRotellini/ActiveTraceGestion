import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import EquiposListPage from '@/features/equipos-docentes/pages/EquiposListPage'
import EquipoFormPage from '@/features/equipos-docentes/pages/EquipoFormPage'
import { AsignacionMasivaModal } from '@/features/equipos-docentes/components/AsignacionMasivaModal'
import { ClonarModal } from '@/features/equipos-docentes/components/ClonarModal'

describe('EquiposDocentes', () => {
  it('EquiposListPage renders title and new button', () => {
    render(<EquiposListPage />)
    expect(screen.getByText('Equipos Docentes')).toBeInTheDocument()
    expect(screen.getByText('Nueva asignación')).toBeInTheDocument()
  })

  it('EquipoFormPage renders creation form', () => {
    render(<EquipoFormPage />)
    expect(screen.getByText('Nueva asignacion de equipo')).toBeInTheDocument()
    expect(screen.getByText('Crear asignacion')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
  })

  it('AsignacionMasivaModal renders form fields', () => {
    render(<AsignacionMasivaModal onClose={() => {}} />)
    expect(screen.getByText('Asignacion masiva')).toBeInTheDocument()
    expect(screen.getByText('Asignar')).toBeInTheDocument()
  })

  it('ClonarModal renders clone form', () => {
    render(<ClonarModal onClose={() => {}} />)
    expect(screen.getByText('Clonar Equipo')).toBeInTheDocument()
    expect(screen.getByText('Clonar')).toBeInTheDocument()
  })
})
