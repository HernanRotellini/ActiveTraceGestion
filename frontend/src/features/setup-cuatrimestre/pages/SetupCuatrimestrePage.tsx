import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { usePeriodosList, useCrearPeriodo, useActivarPeriodo, useDesactivarPeriodo } from '@/features/setup-cuatrimestre/hooks/usePeriodos'

export default function SetupCuatrimestrePage() {
  const { data, isLoading } = usePeriodosList()
  const crearPeriodo = useCrearPeriodo()
  const activarPeriodo = useActivarPeriodo()
  const desactivarPeriodo = useDesactivarPeriodo()

  const [showForm, setShowForm] = useState(false)
  const [nombre, setNombre] = useState('')
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [error, setError] = useState('')

  const handleCrear = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!nombre.trim() || !fechaInicio || !fechaFin) {
      setError('Complete todos los campos.')
      return
    }
    try {
      await crearPeriodo.mutateAsync({ nombre: nombre.trim(), fecha_inicio: fechaInicio, fecha_fin: fechaFin })
      setShowForm(false)
      setNombre('')
      setFechaInicio('')
      setFechaFin('')
    } catch {
      setError('Error al crear el período.')
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Setup de Cuatrimestre</h1>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancelar' : 'Nuevo Período'}
        </Button>
      </div>

      {showForm && (
        <Card className="p-6">
          <form onSubmit={handleCrear} className="space-y-4">
            {error && <Alert variant="error">{error}</Alert>}
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Nombre del período</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Ej: 1C 2026"
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Fecha inicio</label>
                <input
                  type="date"
                  value={fechaInicio}
                  onChange={(e) => setFechaInicio(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Fecha fin</label>
                <input
                  type="date"
                  value={fechaFin}
                  onChange={(e) => setFechaFin(e.target.value)}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button type="submit" loading={crearPeriodo.isPending}>Crear Período</Button>
            </div>
          </form>
        </Card>
      )}

      <div className="space-y-4">
        {data?.items.map((periodo) => (
          <Card key={periodo.id} className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{periodo.nombre}</h3>
                <p className="text-sm text-gray-500">
                  {new Date(periodo.fecha_inicio).toLocaleDateString()} - {new Date(periodo.fecha_fin).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                  periodo.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>{periodo.activo ? 'Activo' : 'Inactivo'}</span>
                {periodo.activo ? (
                  <Button variant="secondary" onClick={() => desactivarPeriodo.mutate(periodo.id)}>
                    Desactivar
                  </Button>
                ) : (
                  <Button onClick={() => activarPeriodo.mutate(periodo.id)}>
                    Activar
                  </Button>
                )}
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-xs font-medium uppercase text-gray-500 mb-2">Fechas Académicas ({periodo.fechas?.length ?? 0})</h4>
                {periodo.fechas && periodo.fechas.length > 0 ? (
                  <div className="space-y-1">
                    {periodo.fechas.map((f) => (
                      <div key={f.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700">{f.label} ({f.key})</span>
                        <span className="text-gray-500">{new Date(f.fecha).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Sin fechas cargadas.</p>
                )}
              </div>
              <div>
                <h4 className="text-xs font-medium uppercase text-gray-500 mb-2">Programas ({periodo.programas?.length ?? 0})</h4>
                {periodo.programas && periodo.programas.length > 0 ? (
                  <div className="space-y-1">
                    {periodo.programas.map((p) => (
                      <div key={p.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700">{p.materia_nombre}</span>
                        <span className="text-gray-500">{p.carrera} - A{p.anio}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Sin programas asignados.</p>
                )}
              </div>
            </div>
          </Card>
        ))}
        {(!data?.items || data.items.length === 0) && (
          <Card className="p-12 text-center">
            <p className="text-gray-500">No hay períodos académicos registrados.</p>
          </Card>
        )}
      </div>
    </div>
  )
}
