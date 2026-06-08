import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { TrackingBadge } from '@/features/comunicaciones/components/TrackingBadge'

describe('TrackingBadge', () => {
  it('shows correct label and color for pendiente', () => {
    render(<TrackingBadge estado="pendiente" />)
    const badge = screen.getByText('Pendiente')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('yellow')
  })

  it('shows correct label and color for enviado', () => {
    render(<TrackingBadge estado="enviado" />)
    const badge = screen.getByText('Enviado')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('green')
  })

  it('shows correct label and color for fallido', () => {
    render(<TrackingBadge estado="fallido" />)
    const badge = screen.getByText('Fallido')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('red')
  })

  it('shows correct label and color for cancelado', () => {
    render(<TrackingBadge estado="cancelado" />)
    const badge = screen.getByText('Cancelado')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('gray')
  })
})
