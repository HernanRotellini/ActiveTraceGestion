import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Spinner } from '@/shared/components/Spinner'
import { useCarreras, useCohortes, useMaterias, useCrearMateria, useActualizarMateria } from '@/features/admin/hooks/useAdmin'
import type { Materia, MateriaPayload } from '@/features/admin/types'

export default function MateriasPage() {
  const { data: carreras } = useCarreras()
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const { data: cohortes } = useCohortes(carreraId || undefined)
  const { data, isLoading } = useMaterias(carreraId || undefined, cohorteId || undefined)
  const crear = useCrearMateria()
  const [editId, setEditId] = useState<string | null>(null)
  const [nombre, setNombre] = useState('')
  const [codigo, setCodigo] = useState('')
  const [cargaHoraria, setCargaHoraria] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState('')

  const resetForm = () => {
    setNombre('')
    setCodigo('')
    setCargaHoraria('')
    setEditId(null)
    setShowForm(false)
    setError('')
  }

  const handleEdit = (m: Materia) => {
    setEditId(m.id)
    setNombre(m.nombre)
    setCodigo(m.codigo)
    setCargaHoraria(m.carga_horaria.toString())
    setShowForm(true)
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!nombre.trim() || !codigo.trim() || !cargaHoraria || !carreraId || !cohorteId) {
      setError('Nombre, código, carga horaria, carrera y cohorte son obligatorios.')
      return
    }
    try {
      const payload: MateriaPayload = {
        carrera_id: carreraId,
        cohorte_id: cohorteId,
        nombre: nombre.trim(),
        codigo: codigo.trim(),
        carga_horaria: Number(cargaHoraria),
      }
      if (editId) {
        const actualizar = useActualizarMateria(editId)
        await actualizar.mutateAsync(payload)
      } else {
        await crear.mutateAsync(payload)
      }
      resetForm()
    } catch {
      setError('Error al guardar la materia.')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Materias</h1>
        <Button onClick={() => { resetForm(); setShowForm(true) }} disabled={!carreraId || !cohorteId}>
          Nueva materia
        </Button>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Carrera</label>
            <select
              value={carreraId}
              onChange={(e) => { setCarreraId(e.target.value); setCohorteId(''); resetForm() }}
              className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todas</option>
              {carreras?.items.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Cohorte</label>
            <select
              value={cohorteId}
              onChange={(e) => { setCohorteId(e.target.value); resetForm() }}
              disabled={!carreraId}
              className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
            >
              <option value="">Todos</option>
              {cohortes?.items.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {showForm && carreraId && cohorteId && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">{editId ? 'Editar materia' : 'Nueva materia'}</h3>
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
                <label className="block text-sm font-medium text-gray-700">Código *</label>
                <input
                  type="text"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Carga horaria *</label>
                <input
                  type="number"
                  value={cargaHoraria}
                  onChange={(e) => setCargaHoraria(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                  min={1}
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
                <th className="px-4 py-3 text-left font-medium text-gray-600">Código</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Carrera</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Cohorte</th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">Carga horaria</th>
                <th className="px-4 py-3 text-center font-medium text-gray-600">Activo</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data?.items.map((m) => (
                <tr key={m.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{m.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{m.codigo}</td>
                  <td className="px-4 py-3 text-gray-500">{m.carrera_nombre ?? '-'}</td>
                  <td className="px-4 py-3 text-gray-500">{m.cohorte_nombre ?? '-'}</td>
                  <td className="px-4 py-3 text-right">{m.carga_horaria}h</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs ${m.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {m.activo ? 'Sí' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" onClick={() => handleEdit(m)}>Editar</Button>
                  </td>
                </tr>
              ))}
              {(!data?.items || data.items.length === 0) && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">No hay materias registradas.</td></tr>
              )}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
