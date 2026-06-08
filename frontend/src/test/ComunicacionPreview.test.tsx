import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import { ComunicacionPreview } from '@/features/comunicaciones/components/ComunicacionPreview'

describe('ComunicacionPreview', () => {
  it('shows subject and body', () => {
    render(
      <ComunicacionPreview
        asunto="Aviso importante"
        cuerpo="Estimado alumno, le informamos que..."
        destinatariosCount={25}
      />,
    )
    expect(screen.getByText('Aviso importante')).toBeInTheDocument()
    expect(screen.getByText('Estimado alumno, le informamos que...')).toBeInTheDocument()
    expect(screen.getByText(/se enviará a/i)).toBeInTheDocument()
    expect(screen.getByText('25')).toBeInTheDocument()
  })
})
