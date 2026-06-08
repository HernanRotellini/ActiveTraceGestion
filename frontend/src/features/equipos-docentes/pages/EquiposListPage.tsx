import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useEquiposList } from '@/features/equipos-docentes/hooks/useEquipos'
import { ExportCsvButton } from '@/features/equipos-docentes/components/ExportCsvButton'
import type { EquiposFilters } from '@/features/equipos-docentes/types'

export default function EquiposListPage() {
  const [filters, setFilters] = useState<EquiposFilters>({ page: 1, limit: 20 })
  const { data, isLoading } = useEquiposList(filters)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Equipos Docentes</h1>
        <div className="flex items-center gap-3">
          <ExportCsvButton filters={filters} />
          <Link
            to="/coordinacion/equipos-docentes/nuevo"
            className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
          >
            Nuevo Equipo
          </Link>
        </div>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Materia</label>
            <input
              type="text"
              value={filters.materia ?? ''}
              onChange={(e) => setFilters({ ...filters, materia: e.target.value || undefined, page: 1 })}
              placeholder="Buscar materia..."
              className="block w-48 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Carrera</label>
            <input
              type="text"
              value={filters.carrera ?? ''}
              onChange={(e) => setFilters({ ...filters, carrera: e.target.value || undefined, page: 1 })}
              placeholder="Buscar carrera..."
              className="block w-48 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Estado</label>
            <select
              value={filters.estado ?? ''}
              onChange={(e) => setFilters({ ...filters, estado: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Materia</th>
                  <th className="px-4 py-3">Carrera</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Asignaciones</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data?.items.map((eq) => (
                  <tr key={eq.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{eq.materia_nombre}</td>
                    <td className="px-4 py-3 text-gray-600">{eq.carrera}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        eq.estado === 'activo' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {eq.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{eq.asignaciones?.length ?? 0}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/coordinacion/equipos-docentes/${eq.id}`}
                        className="text-primary-600 hover:text-primary-800 font-medium"
                      >
                        Ver
                      </Link>
                    </td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                      No hay equipos docentes registrados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {data && data.total > (filters.limit ?? 20) && (
            <div className="flex items-center justify-between border-t px-4 py-3">
              <span className="text-sm text-gray-600">
                {((filters.page ?? 1) - 1) * (filters.limit ?? 20) + 1}-{Math.min((filters.page ?? 1) * (filters.limit ?? 20), data.total)} de {data.total}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) - 1 })}
                  disabled={(filters.page ?? 1) <= 1}
                  className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) + 1 })}
                  disabled={(filters.page ?? 1) * (filters.limit ?? 20) >= data.total}
                  className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
