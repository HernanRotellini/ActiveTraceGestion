import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { EstadoBadge } from '@/features/comunicaciones/components/EstadoBadge'

describe('EstadoBadge', () => {
  it('shows correct label and color for Pendiente', () => {
    render(<EstadoBadge estado="Pendiente" />)
    const badge = screen.getByText('Pendiente')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('yellow')
  })

  it('shows correct label and color for Enviando', () => {
    render(<EstadoBadge estado="Enviando" />)
    const badge = screen.getByText('Enviando')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('blue')
  })

  it('shows correct label and color for Enviado', () => {
    render(<EstadoBadge estado="Enviado" />)
    const badge = screen.getByText('Enviado')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('green')
  })

  it('shows correct label and color for Error', () => {
    render(<EstadoBadge estado="Error" />)
    const badge = screen.getByText('Error')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('red')
  })

  it('shows correct label and color for Cancelado', () => {
    render(<EstadoBadge estado="Cancelado" />)
    const badge = screen.getByText('Cancelado')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('gray')
  })
})
