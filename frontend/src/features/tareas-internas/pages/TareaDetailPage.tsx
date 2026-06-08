import { useParams, Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { useTarea, useCambiarEstadoTarea, useCrearComentario } from '@/features/tareas-internas/hooks/useTareas'
import { ComentarioList } from '@/features/tareas-internas/components/ComentarioList'
import type { TareaEstado } from '@/features/tareas-internas/types'

const ESTADOS: TareaEstado[] = ['pendiente', 'en_progreso', 'completada', 'cancelada']

export default function TareaDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: tarea, isLoading } = useTarea(id!)
  const cambiarEstado = useCambiarEstadoTarea()
  const crearComentario = useCrearComentario(id!)

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

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link to="/coordinacion/tareas" className="text-sm text-primary-600 hover:text-primary-800">&larr; Volver</Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">{tarea.titulo}</h1>
        </div>
        <Link to={`/coordinacion/tareas/${id}/editar`}>
          <Button variant="secondary">Editar</Button>
        </Link>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Estado:</span>
            <span className="ml-2 font-medium text-gray-900">{tarea.estado}</span>
          </div>
          <div>
            <span className="text-gray-500">Prioridad:</span>
            <span className="ml-2 font-medium text-gray-900">{tarea.prioridad}</span>
          </div>
          <div>
            <span className="text-gray-500">Asignado:</span>
            <span className="ml-2 text-gray-900">{tarea.asignado_nombre ?? 'Sin asignar'}</span>
          </div>
          <div>
            <span className="text-gray-500">Fecha límite:</span>
            <span className="ml-2 text-gray-900">{tarea.fecha_limite ? new Date(tarea.fecha_limite).toLocaleDateString() : 'Sin fecha'}</span>
          </div>
          <div>
            <span className="text-gray-500">Creado por:</span>
            <span className="ml-2 text-gray-900">{tarea.creador_nombre}</span>
          </div>
          <div>
            <span className="text-gray-500">Creado:</span>
            <span className="ml-2 text-gray-900">{new Date(tarea.creado_en).toLocaleDateString()}</span>
          </div>
        </div>

        {tarea.descripcion && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700">Descripción</h3>
            <p className="mt-1 text-sm text-gray-800 whitespace-pre-wrap">{tarea.descripcion}</p>
          </div>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          {estadosDisponibles.map((est) => (
            <Button
              key={est}
              variant="secondary"
              size="sm"
              onClick={() => cambiarEstado.mutate({ id: tarea.id, estado: est })}
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
          onSubmit={async (payload) => { await crearComentario.mutateAsync(payload) }}
          loading={crearComentario.isPending}
        />
      </Card>
    </div>
  )
}
