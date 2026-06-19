import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import AvisosListPage from '@/features/avisos/pages/AvisosListPage'
import AvisoFormPage from '@/features/avisos/pages/AvisoFormPage'
import { AckProgressBar } from '@/features/avisos/components/AckProgressBar'

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
    render(<AckProgressBar total_acks={2} sin_confirmar={2} />)
    expect(screen.getByText('2/4 (50%)')).toBeInTheDocument()
  })

  it('AckProgressBar handles zero confirmations', () => {
    render(<AckProgressBar total_acks={0} sin_confirmar={0} />)
    expect(screen.getByText('0/0 (0%)')).toBeInTheDocument()
  })
})
