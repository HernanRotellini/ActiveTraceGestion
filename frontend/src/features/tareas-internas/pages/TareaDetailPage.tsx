import { useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { useTarea, useCambiarEstadoTarea, useCrearComentario } from '@/features/tareas-internas/hooks/useTareas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import { ComentarioList } from '@/features/tareas-internas/components/ComentarioList'
import type { TareaEstado } from '@/features/tareas-internas/types'

const ESTADOS: TareaEstado[] = ['Pendiente', 'En progreso', 'Resuelta', 'Cancelada']

const ESTADO_CLASSES: Record<TareaEstado, string> = {
  'Pendiente': 'bg-yellow-100 text-yellow-700',
  'En progreso': 'bg-blue-100 text-blue-700',
  'Resuelta': 'bg-green-100 text-green-700',
  'Cancelada': 'bg-gray-100 text-gray-600',
}

export default function TareaDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: tarea, isLoading } = useTarea(id!)
  const cambiarEstado = useCambiarEstadoTarea()
  const crearComentario = useCrearComentario(id!)
  const { data: usuariosResp } = useUsuarios()
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const usuariosById = useMemo(
    () => new Map((usuariosResp?.items ?? []).map((u) => [u.id, `${u.nombre} ${u.apellidos}`])),
    [usuariosResp?.items],
  )

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (!tarea) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Tarea no encontrada</h1>
        <Link to="/coordinacion/tareas" className="text-primary-600 hover:text-primary-800">Volver</Link>
      </div>
    )
  }

  const estadosDisponibles = ESTADOS.filter((e) => e !== tarea.estado)

  const handleCambiarEstado = async (estado: TareaEstado) => {
    try {
      await cambiarEstado.mutateAsync({ id: tarea.id, estado })
      setToast({ message: `Estado actualizado a "${estado}".`, variant: 'success' })
    } catch {
      setToast({ message: 'No se pudo cambiar el estado.', variant: 'error' })
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/tareas" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
          <h1 className="mt-1 text-2xl font-bold text-gray-900">{tarea.titulo}</h1>
        </div>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className={`ml-2 inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_CLASSES[tarea.estado] ?? 'bg-gray-100 text-gray-600'}`}>
              {tarea.estado}
            </span>
          </div>
          <div>
            <span className="text-gray-500">Asignado a:</span>
            <span className="ml-2 text-gray-900">{usuariosById.get(tarea.asignado_a) ?? tarea.asignado_a.slice(0, 8)}</span>
          </div>
          <div>
            <span className="text-gray-500">Asignado por:</span>
            <span className="ml-2 text-gray-900">{usuariosById.get(tarea.asignado_por) ?? tarea.asignado_por.slice(0, 8)}</span>
          </div>
          <div>
            <span className="text-gray-500">Creada:</span>
            <span className="ml-2 text-gray-900">{new Date(tarea.created_at).toLocaleDateString()}</span>
          </div>
          {tarea.updated_at && (
            <div>
              <span className="text-gray-500">Actualizada:</span>
              <span className="ml-2 text-gray-900">{new Date(tarea.updated_at).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        {tarea.descripcion && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700">Descripción</h3>
            <p className="mt-1 whitespace-pre-wrap text-sm text-gray-800">{tarea.descripcion}</p>
          </div>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          {estadosDisponibles.map((est) => (
            <Button
              key={est}
              variant="secondary"
              size="sm"
              onClick={() => handleCambiarEstado(est)}
              loading={cambiarEstado.isPending}
            >
              Marcar como {est}
            </Button>
          ))}
        </div>
      </Card>

      <h2 className="text-lg font-semibold text-gray-900">Comentarios</h2>
      <Card className="p-4">
        <ComentarioList
          comentarios={tarea.comentarios ?? []}
          usuariosById={usuariosById}
          onSubmit={async (payload) => { await crearComentario.mutateAsync(payload) }}
          loading={crearComentario.isPending}
        />
      </Card>
    </div>
  )
}
