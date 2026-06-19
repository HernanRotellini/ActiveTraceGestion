import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import type { ComentarioResponse, ComentarioPayload } from '@/features/tareas-internas/types'

interface ComentarioListProps {
  comentarios: ComentarioResponse[]
  usuariosById?: Map<string, string>
  onSubmit: (payload: ComentarioPayload) => Promise<void>
  loading?: boolean
}

function shortId(id: string) {
  return id.slice(0, 8)
}

export function ComentarioList({ comentarios, usuariosById, onSubmit, loading }: ComentarioListProps) {
  const [texto, setTexto] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!texto.trim()) return
    await onSubmit({ texto: texto.trim() })
    setTexto('')
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Agregar comentario..."
          className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <Button type="submit" loading={loading}>Enviar</Button>
      </form>

      {comentarios.map((com) => (
        <Card key={com.id} className="p-3">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span className="font-medium text-gray-700">
              {usuariosById?.get(com.autor_id) ?? shortId(com.autor_id)}
            </span>
            <span>{new Date(com.created_at).toLocaleString()}</span>
          </div>
          <p className="mt-1 text-sm text-gray-800">{com.texto}</p>
        </Card>
      ))}

      {comentarios.length === 0 && (
        <p className="text-center text-sm text-gray-500">Sin comentarios.</p>
      )}
    </div>
  )
}
