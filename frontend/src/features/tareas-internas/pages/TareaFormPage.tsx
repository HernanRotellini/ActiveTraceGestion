import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import { Combobox } from '@/shared/components/Combobox'
import { useCrearTarea } from '@/features/tareas-internas/hooks/useTareas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'

export default function TareaFormPage() {
  const navigate = useNavigate()
  const crear = useCrearTarea()

  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [asignadoId, setAsignadoId] = useState('')
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} ${u.apellidos} (${u.email})`,
  }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!titulo.trim()) {
      setToast({ message: 'El título es obligatorio.', variant: 'error' })
      return
    }
    if (!asignadoId) {
      setToast({ message: 'Debe seleccionar un usuario asignado.', variant: 'error' })
      return
    }
    try {
      await crear.mutateAsync({
        titulo: titulo.trim(),
        descripcion: descripcion.trim(),
        asignado_a: asignadoId,
      })
      setToast({ message: 'Tarea creada correctamente.', variant: 'success' })
      window.setTimeout(() => navigate('/coordinacion/tareas'), 800)
    } catch {
      setToast({ message: 'Error al crear la tarea.', variant: 'error' })
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <h1 className="text-2xl font-bold text-gray-900">Nueva Tarea</h1>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
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

          <Combobox
            label="Asignado a *"
            items={usuarioItems}
            value={asignadoId}
            onChange={setAsignadoId}
            placeholder="Buscar usuario..."
            isLoading={loadingUsuarios}
          />

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => navigate('/coordinacion/tareas')}>Cancelar</Button>
            <Button type="submit" loading={crear.isPending}>
              Crear tarea
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
