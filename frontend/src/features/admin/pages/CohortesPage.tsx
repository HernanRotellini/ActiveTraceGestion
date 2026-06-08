import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Spinner } from '@/shared/components/Spinner'
import { useCarreras, useCohortes, useCrearCohorte, useActualizarCohorte } from '@/features/admin/hooks/useAdmin'
import type { Cohorte, CohortePayload } from '@/features/admin/types'

export default function CohortesPage() {
  const { data: carreras } = useCarreras()
  const [carreraId, setCarreraId] = useState('')
  const { data, isLoading } = useCohortes(carreraId || undefined)
  const crear = useCrearCohorte()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [anio, setAnio] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')

  const resetForm = () => {
    setNombre('')
    setAnio('')
    setEditId(null)
    setShowForm(false)
    setError('')
  }

  const handleEdit = (c: Cohorte) => {
    setEditId(c.id)
    setNombre(c.nombre)
    setAnio(c.anio.toString())
    setShowForm(true)
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!nombre.trim() || !anio || !carreraId) {
      setError('Nombre, año y carrera son obligatorios.')
      return
    }
    try {
      const payload: CohortePayload = { carrera_id: carreraId, nombre: nombre.trim(), anio: Number(anio) }
      if (editId) {
        const actualizar = useActualizarCohorte(editId)
        await actualizar.mutateAsync(payload)
      } else {
        await crear.mutateAsync(payload)
      }
      resetForm()
    } catch {
      setError('Error al guardar la cohorte.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Cohortes</h1>
        <Button onClick={() => { resetForm(); setShowForm(true) }} disabled={!carreraId}>
          Nueva cohorte
        </Button>
      </div>

      <Card className="p-4">
        <div className="space-y-1 max-w-xs">
          <label className="block text-xs font-medium text-gray-600">Carrera *</label>
          <select
            value={carreraId}
            onChange={(e) => { setCarreraId(e.target.value); resetForm() }}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Seleccione una carrera</option>
            {carreras?.items.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
      </Card>

      {showForm && carreraId && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar cohorte' : 'Nueva cohorte'}</h3>
          <form onSubmit={handleSave} className="space-y-4">
            {error && <Alert variant="error">{error}</Alert>}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Nombre *</label>
                <input
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Año *</label>
                <input
                  type="number"
                  value={anio}
                  onChange={(e) => setAnio(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                  min={2000}
                  max={2100}
                />
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={resetForm} type="button">Cancelar</Button>
              <Button type="submit" loading={crear.isPending}>{editId ? 'Actualizar' : 'Crear'}</Button>
            </div>
          </form>
        </Card>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Nombre</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Año</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{c.anio}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${c.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {c.activo ? 'Sí' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" onClick={() => handleEdit(c)}>Editar</Button>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-500">No hay cohortes registradas.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
