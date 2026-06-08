import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import type { Comentario, ComentarioPayload } from '@/features/tareas-internas/types'

interface ComentarioListProps {
  comentarios: Comentario[]
  onSubmit: (payload: ComentarioPayload) => Promise<void>
  loading?: boolean
}

export function ComentarioList({ comentarios, onSubmit, loading }: ComentarioListProps) {
  const [contenido, setContenido] = useState('')
  const [responderA, setResponderA] = useState<string | null>(null)
  const [respuesta, setRespuesta] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!contenido.trim()) return
    await onSubmit({ contenido: contenido.trim() })
    setContenido('')
  }

  const handleResponder = async (padreId: string) => {
    if (!respuesta.trim()) return
    await onSubmit({ contenido: respuesta.trim(), padre_id: padreId })
    setRespuesta('')
    setResponderA(null)
  }

  const principales = comentarios.filter((c) => !c.padre_id)

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={contenido}
          onChange={(e) => setContenido(e.target.value)}
          placeholder="Agregar comentario..."
          className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <Button type="submit" loading={loading}>Enviar</Button>
      </form>

      {principales.map((com) => (
        <div key={com.id}>
          <Card className="p-3">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span className="font-medium text-gray-700">{com.autor_nombre}</span>
              <span>{new Date(com.creado_en).toLocaleString()}</span>
            </div>
            <p className="mt-1 text-sm text-gray-800">{com.contenido}</p>
            <button
              type="button"
              onClick={() => setResponderA(responderA === com.id ? null : com.id)}
              className="mt-1 text-xs text-primary-600 hover:text-primary-800"
            >
              {responderA === com.id ? 'Cancelar' : 'Responder'}
            </button>
          </Card>

          {responderA === com.id && (
            <div className="ml-6 mt-2 flex gap-2">
              <input
                type="text"
                value={respuesta}
                onChange={(e) => setRespuesta(e.target.value)}
                placeholder="Escribir respuesta..."
                className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <Button size="sm" onClick={() => handleResponder(com.id)} loading={loading}>Responder</Button>
            </div>
          )}

          {comentarios
            .filter((c) => c.padre_id === com.id)
            .map((resp) => (
              <div key={resp.id} className="ml-6 mt-2">
                <Card className="border-l-4 border-l-primary-200 p-3">
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="font-medium text-gray-700">{resp.autor_nombre}</span>
                    <span>{new Date(resp.creado_en).toLocaleString()}</span>
                  </div>
                  <p className="mt-1 text-sm text-gray-800">{resp.contenido}</p>
                </Card>
              </div>
            ))}
        </div>
      ))}

      {principales.length === 0 && (
        <p className="text-center text-sm text-gray-500">Sin comentarios.</p>
      )}
    </div>
  )
}
