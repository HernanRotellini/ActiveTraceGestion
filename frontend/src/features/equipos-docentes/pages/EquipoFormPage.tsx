import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { useEquipo, useCrearEquipo, useActualizarEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import { Spinner } from '@/shared/components/Spinner'

export default function EquipoFormPage() {
  const { id } = useParams<{ id: string }>()
  const isEdit = !!id
  const navigate = useNavigate()

  const { data: equipo, isLoading: loadingEquipo } = useEquipo(id ?? '')
  const crearEquipo = useCrearEquipo()
  const actualizarEquipo = useActualizarEquipo(id ?? '')

  const [materiaId, setMateriaId] = useState('')
  const [carrera, setCarrera] = useState('')
  const [error, setError] = useState('')

  useState(() => {
    if (equipo) {
      setMateriaId(equipo.materia_id)
      setCarrera(equipo.carrera)
    }
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!materiaId.trim() || !carrera.trim()) {
      setError('Complete todos los campos obligatorios.')
      return
    }
    try {
      if (isEdit) {
        await actualizarEquipo.mutateAsync({ materia_id: materiaId, carrera })
      } else {
        await crearEquipo.mutateAsync({ materia_id: materiaId, carrera })
      }
      navigate('/coordinacion/equipos-docentes')
    } catch {
      setError('Error al guardar el equipo.')
    }
  }

  if (isEdit && loadingEquipo) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">
        {isEdit ? 'Editar Equipo' : 'Nuevo Equipo'}
      </h1>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Materia *</label>
            <input
              type="text"
              value={materiaId}
              onChange={(e) => setMateriaId(e.target.value)}
              placeholder="ID de materia"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Carrera *</label>
            <input
              type="text"
              value={carrera}
              onChange={(e) => setCarrera(e.target.value)}
              placeholder="Nombre de carrera"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
              required
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => navigate('/coordinacion/equipos-docentes')}>
              Cancelar
            </Button>
            <Button type="submit" loading={crearEquipo.isPending || actualizarEquipo.isPending}>
              {isEdit ? 'Guardar cambios' : 'Crear equipo'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
