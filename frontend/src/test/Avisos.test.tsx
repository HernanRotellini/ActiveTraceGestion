import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import AvisosListPage from '@/features/avisos/pages/AvisosListPage'
import AvisoFormPage from '@/features/avisos/pages/AvisoFormPage'
import { AckProgressBar } from '@/features/avisos/components/AckProgressBar'
import type { AckStatus } from '@/features/avisos/types'

const mockAcks: AckStatus[] = [
  { usuario_id: '1', usuario_nombre: 'Juan', leido: true, leido_en: '2026-01-15T10:00:00Z' },
  { usuario_id: '2', usuario_nombre: 'María', leido: false },
  { usuario_id: '3', usuario_nombre: 'Pedro', leido: true, leido_en: '2026-01-15T11:00:00Z' },
  { usuario_id: '4', usuario_nombre: 'Ana', leido: false },
]

describe('Avisos', () => {
  it('AvisosListPage renders title and new button', () => {
    render(<AvisosListPage />)
    expect(screen.getByText('Avisos')).toBeInTheDocument()
    expect(screen.getByText('Nuevo Aviso')).toBeInTheDocument()
  })

  it('AvisoFormPage renders creation form', () => {
    render(<AvisoFormPage />)
    expect(screen.getByText('Nuevo Aviso')).toBeInTheDocument()
    expect(screen.getByText('Crear aviso')).toBeInTheDocument()
  })

  it('AckProgressBar shows correct stats', () => {
    render(<AckProgressBar acks={mockAcks} />)
    expect(screen.getByText('2/4 (50%)')).toBeInTheDocument()
  })

  it('AckProgressBar handles empty acks', () => {
    render(<AckProgressBar acks={[]} />)
    expect(screen.getByText('0/0 (0%)')).toBeInTheDocument()
  })
})
