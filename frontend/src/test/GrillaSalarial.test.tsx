import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import GrillaSalarialPage from '@/features/liquidaciones/pages/GrillaSalarialPage'

describe('GrillaSalarialPage', () => {
  it('renders title and tabs', () => {
    render(<GrillaSalarialPage />)
    expect(screen.getByText('Grilla Salarial')).toBeInTheDocument()
    expect(screen.getByText('Salarios Base')).toBeInTheDocument()
    expect(screen.getByText('Plus')).toBeInTheDocument()
  })

  it('renders nuevo button', () => {
    render(<GrillaSalarialPage />)
    expect(screen.getByText('Nuevo')).toBeInTheDocument()
  })
})
