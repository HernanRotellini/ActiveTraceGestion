import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Combobox } from '@/shared/components/Combobox'
import { useCrearTarea } from '@/features/tareas-internas/hooks/useTareas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'

export default function TareaFormPage() {
  const crear = useCrearTarea()

  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [asignadoId, setAsignadoId] = useState('')
  const [error, setError] = useState('')

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} (${u.email})`,
  }))

  // Removed useEffect for fetching edit data since edit is not supported

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!titulo.trim()) {
      setError('El título es obligatorio.')
      return
    }
    if (!asignadoId) {
      setError('Debe seleccionar un usuario asignado.')
      return
    }
    try {
      const base = {
        titulo: titulo.trim(),
        descripcion: descripcion.trim(),
        asignado_a: asignadoId,
      }
      await crear.mutateAsync(base)
      navigate('/coordinacion/tareas')
    } catch {
      setError('Error al crear la tarea.')
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Nueva Tarea</h1>

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

          <Combobox
            label="Asignado a *"
            items={usuarioItems}
            value={asignadoId}
            onChange={setAsignadoId}
            placeholder="Buscar usuario..."
            isLoading={loadingUsuarios}
          />
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => navigate('/coordinacion/tareas')}>Cancelar</Button>
            <Button type="submit" loading={crear.isPending}>
              Crear tarea
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
