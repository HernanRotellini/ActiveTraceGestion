import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { useAdminInstancias, useActualizarInstancia } from '@/features/encuentros/hooks/useEncuentros'
import type { EstadoInstancia, InstanciaEncuentroUpdate } from '@/features/encuentros/types'

const ESTADOS: EstadoInstancia[] = ['Programado', 'Realizado', 'Cancelado']

const ESTADO_CLASSES: Record<EstadoInstancia, string> = {
  Programado: 'bg-blue-100 text-blue-700',
  Realizado: 'bg-green-100 text-green-700',
  Cancelado: 'bg-gray-100 text-gray-600',
}

export default function EncuentroDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: instancias, isLoading } = useAdminInstancias()
  const actualizar = useActualizarInstancia()
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const instancia = (instancias ?? []).find((i) => i.id === id)

  const [form, setForm] = useState<InstanciaEncuentroUpdate>({})

  const handleSave = async () => {
    if (!id) return
    try {
      await actualizar.mutateAsync({ id, update: form })
      setToast({ message: 'Encuentro actualizado.', variant: 'success' })
    } catch {
      setToast({ message: 'Error al actualizar el encuentro.', variant: 'error' })
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!instancia) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-900">Encuentro no encontrado</h1>
        <Link to="/coordinacion/encuentros" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <div>
        <Link to="/coordinacion/encuentros" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
        <h1 className="mt-1 text-2xl font-bold text-gray-900">{instancia.titulo}</h1>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_CLASSES[instancia.estado] ?? 'bg-gray-100 text-gray-600'}`}>
              {instancia.estado}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Fecha:</span>
            <span className="ml-2 text-gray-900">{new Date(instancia.fecha).toLocaleDateString()}</span>
          </div>
          <div>
            <span className="text-gray-500">Hora:</span>
            <span className="ml-2 text-gray-900">{instancia.hora}</span>
          </div>
          {instancia.meet_url && (
            <div>
              <span className="text-gray-500">Meet:</span>
              <a href={instancia.meet_url} target="_blank" rel="noreferrer" className="ml-2 text-primary-600 hover:text-primary-800">Enlace</a>
            </div>
          )}
          {instancia.video_url && (
            <div>
              <span className="text-gray-500">Grabación:</span>
              <a href={instancia.video_url} target="_blank" rel="noreferrer" className="ml-2 text-primary-600 hover:text-primary-800">Ver grabación</a>
            </div>
          )}
          {instancia.comentario && (
            <div className="col-span-2">
              <span className="text-gray-500">Comentario:</span>
              <p className="mt-1 text-gray-800">{instancia.comentario}</p>
            </div>
          )}
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Editar</h2>
      <Card className="p-6">
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Estado</label>
            <select
              value={form.estado ?? instancia.estado}
              onChange={(e) => setForm({ ...form, estado: e.target.value as EstadoInstancia })}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {ESTADOS.map((est) => <option key={est} value={est}>{est}</option>)}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Link Meet</label>
            <input
              type="url"
              value={form.meet_url ?? instancia.meet_url ?? ''}
              onChange={(e) => setForm({ ...form, meet_url: e.target.value || undefined })}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="https://..."
            />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Link Grabación</label>
            <input
              type="url"
              value={form.video_url ?? instancia.video_url ?? ''}
              onChange={(e) => setForm({ ...form, video_url: e.target.value || undefined })}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="https://..."
            />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Comentario interno</label>
            <textarea
              value={form.comentario ?? instancia.comentario ?? ''}
              onChange={(e) => setForm({ ...form, comentario: e.target.value || undefined })}
              rows={3}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="flex justify-end">
            <Button onClick={handleSave} loading={actualizar.isPending}>Guardar cambios</Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
