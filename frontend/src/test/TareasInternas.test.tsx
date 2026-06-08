import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@/test/test-utils'
import TareasListPage from '@/features/tareas-internas/pages/TareasListPage'
import TareaFormPage from '@/features/tareas-internas/pages/TareaFormPage'
import { ComentarioList } from '@/features/tareas-internas/components/ComentarioList'
import type { Comentario } from '@/features/tareas-internas/types'

const mockComentarios: Comentario[] = [
  { id: '1', tarea_id: 't1', autor_id: 'u1', autor_nombre: 'Carlos', contenido: 'Comentario principal', creado_en: '2026-01-10T10:00:00Z' },
  { id: '2', tarea_id: 't1', autor_id: 'u2', autor_nombre: 'Laura', contenido: 'Respuesta', creado_en: '2026-01-10T11:00:00Z', padre_id: '1' },
]

describe('TareasInternas', () => {
  it('TareasListPage renders title and new button', () => {
    render(<TareasListPage />)
    expect(screen.getByText('Tareas Internas')).toBeInTheDocument()
    expect(screen.getByText('Nueva Tarea')).toBeInTheDocument()
  })

  it('TareaFormPage renders creation form', () => {
    render(<TareaFormPage />)
    expect(screen.getByText('Nueva Tarea')).toBeInTheDocument()
    expect(screen.getByText('Crear tarea')).toBeInTheDocument()
  })

  it('ComentarioList muestra comentarios y respuestas', () => {
    render(<ComentarioList comentarios={mockComentarios} onSubmit={async () => {}} />)
    expect(screen.getByText('Comentario principal')).toBeInTheDocument()
    expect(screen.getByText('Respuesta')).toBeInTheDocument()
  })

  it('ComentarioList muestra empty state', () => {
    render(<ComentarioList comentarios={[]} onSubmit={async () => {}} />)
    expect(screen.getByText('Sin comentarios.')).toBeInTheDocument()
  })
})
