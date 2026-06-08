import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import type { MonitorFilters } from '@/features/monitores/types/monitores'

interface MetricResumen {
  total_alumnos: number
  total_comisiones: number
  promedio_atraso: number
  entregas_pendientes: number
}

interface AtrasoPorMateria {
  materia_id: string
  materia_nombre: string
  total_alumnos: number
  atrasados: number
  entregados: number
  porcentaje_atraso: number
}

export default function MonitorGeneralPage() {
  const [filters, setFilters] = useState<MonitorFilters>({})

  const metricas: MetricResumen = {
    total_alumnos: 0,
    total_comisiones: 0,
    promedio_atraso: 0,
    entregas_pendientes: 0,
  }

  const materiasAtraso: AtrasoPorMateria[] = []

  const handleExport = () => {
    // Export CSV
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Monitor General</h1>
        <Button variant="secondary" onClick={handleExport}>Exportar CSV</Button>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Materia</label>
            <input
              type="text"
              value={filters.materia_id ?? ''}
              onChange={(e) => setFilters({ ...filters, materia_id: e.target.value || undefined })}
              placeholder="Filtrar por materia..."
              className="block w-48 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Período</label>
            <input
              type="text"
              value={filters.periodo ?? ''}
              onChange={(e) => setFilters({ ...filters, periodo: e.target.value || undefined })}
              placeholder="Ej: 2026-1"
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Alumnos</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{metricas.total_alumnos}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Comisiones</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{metricas.total_comisiones}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Promedio Atraso</p>
          <p className="mt-1 text-2xl font-bold text-orange-600">{metricas.promedio_atraso}%</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Entregas Pendientes</p>
          <p className="mt-1 text-2xl font-bold text-red-600">{metricas.entregas_pendientes}</p>
        </Card>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
              <tr>
                <th className="px-4 py-3">Materia</th>
                <th className="px-4 py-3">Total Alumnos</th>
                <th className="px-4 py-3">Atrasados</th>
                <th className="px-4 py-3">Entregados</th>
                <th className="px-4 py-3">% Atraso</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {materiasAtraso.map((m) => (
                <tr key={m.materia_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{m.materia_nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{m.total_alumnos}</td>
                  <td className="px-4 py-3 text-red-600">{m.atrasados}</td>
                  <td className="px-4 py-3 text-green-600">{m.entregados}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-20 overflow-hidden rounded-full bg-gray-200">
                        <div
                          className={`h-full rounded-full ${m.porcentaje_atraso > 50 ? 'bg-red-500' : m.porcentaje_atraso > 20 ? 'bg-orange-500' : 'bg-green-500'}`}
                          style={{ width: `${m.porcentaje_atraso}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{m.porcentaje_atraso}%</span>
                    </div>
                  </td>
                </tr>
              ))}
              {materiasAtraso.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    No hay datos disponibles para los filtros seleccionados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
