import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { useTarea, useCrearTarea, useActualizarTarea } from '@/features/tareas-internas/hooks/useTareas'
import { Spinner } from '@/shared/components/Spinner'
import type { Prioridad } from '@/features/tareas-internas/types'

const PRIORIDADES: Prioridad[] = ['baja', 'media', 'alta', 'critica']

export default function TareaFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const navigate = useNavigate()

  const { data: tarea, isLoading: loadingTarea } = useTarea(id ?? '')
  const crear = useCrearTarea()
  const actualizar = useActualizarTarea(id ?? '')

  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [prioridad, setPrioridad] = useState<Prioridad>('media')
  const [asignadoId, setAsignadoId] = useState('')
  const [fechaLimite, setFechaLimite] = useState('')
  const [error, setError] = useState('')

  useState(() => {
    if (tarea) {
      setTitulo(tarea.titulo)
      setDescripcion(tarea.descripcion)
      setPrioridad(tarea.prioridad)
      setAsignadoId(tarea.asignado_id ?? '')
      setFechaLimite(tarea.fecha_limite ? tarea.fecha_limite.slice(0, 10) : '')
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!titulo.trim()) {
      setError('El título es obligatorio.')
      return
    }
    try {
      const payload = {
        titulo: titulo.trim(),
        descripcion: descripcion.trim(),
        prioridad,
        asignado_id: asignadoId || undefined,
        fecha_limite: fechaLimite || undefined,
      }
      if (isEdit) {
        await actualizar.mutateAsync(payload)
      } else {
        await crear.mutateAsync(payload)
      }
      navigate('/coordinacion/tareas')
    } catch {
      setError('Error al guardar la tarea.')
    }
  }

  if (isEdit && loadingTarea) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        {isEdit ? 'Editar Tarea' : 'Nueva Tarea'}
      </h1>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Título *</label>
            <input
              type="text"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Descripción</label>
            <textarea
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              rows={4}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Prioridad</label>
            <select
              value={prioridad}
              onChange={(e) => setPrioridad(e.target.value as Prioridad)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {PRIORIDADES.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Asignado a</label>
            <input
              type="text"
              value={asignadoId}
              onChange={(e) => setAsignadoId(e.target.value)}
              placeholder="ID de usuario"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Fecha límite</label>
            <input
              type="date"
              value={fechaLimite}
              onChange={(e) => setFechaLimite(e.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => navigate('/coordinacion/tareas')}>Cancelar</Button>
            <Button type="submit" loading={crear.isPending || actualizar.isPending}>
              {isEdit ? 'Guardar cambios' : 'Crear tarea'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
