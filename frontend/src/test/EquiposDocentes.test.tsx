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
    expect(screen.getByText('Nuevo Equipo')).toBeInTheDocument()
    expect(screen.getByText('Exportar CSV')).toBeInTheDocument()
  })

  it('EquipoFormPage renders creation form', () => {
    render(<EquipoFormPage />)
    expect(screen.getByText('Nuevo Equipo')).toBeInTheDocument()
    expect(screen.getByText('Crear equipo')).toBeInTheDocument()
    expect(screen.getByText('Cancelar')).toBeInTheDocument()
  })

  it('AsignacionMasivaModal renders form fields', () => {
    render(<AsignacionMasivaModal equipoId="test-id" onClose={() => {}} />)
    expect(screen.getByText('Asignación Masiva')).toBeInTheDocument()
    expect(screen.getByText('Asignar')).toBeInTheDocument()
    expect(screen.getByText('+ Agregar usuario')).toBeInTheDocument()
  })

  it('ClonarModal renders clone form', () => {
    render(<ClonarModal origenEquipoId="test-id" onClose={() => {}} />)
    expect(screen.getByText('Clonar Equipo')).toBeInTheDocument()
    expect(screen.getByText('Clonar')).toBeInTheDocument()
  })
})
