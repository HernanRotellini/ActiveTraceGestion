import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useEncuentrosList } from '@/features/encuentros/hooks/useEncuentros'
import type { EncuentrosFilters } from '@/features/encuentros/types'

export default function EncuentrosListPage() {
  const [filters, setFilters] = useState<EncuentrosFilters>({ page: 1, limit: 20 })
  const { data, isLoading } = useEncuentrosList(filters)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Encuentros</h1>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Fecha desde</label>
            <input
              type="date"
              value={filters.fecha_desde ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value || undefined, page: 1 })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Fecha hasta</label>
            <input
              type="date"
              value={filters.fecha_hasta ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value || undefined, page: 1 })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Materia</label>
            <input
              type="text"
              value={filters.materia_id ?? ''}
              onChange={(e) => setFilters({ ...filters, materia_id: e.target.value || undefined, page: 1 })}
              placeholder="ID de materia"
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Comisión</th>
                  <th className="px-4 py-3">Materia</th>
                  <th className="px-4 py-3">Fecha</th>
                  <th className="px-4 py-3">Aula</th>
                  <th className="px-4 py-3">Slots</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data?.items.map((enc) => (
                  <tr key={enc.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{enc.comision_nombre}</td>
                    <td className="px-4 py-3 text-gray-600">{enc.materia_nombre}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(enc.fecha).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-gray-600">{enc.aula}</td>
                    <td className="px-4 py-3 text-gray-600">{enc.slots?.length ?? 0}</td>
                    <td className="px-4 py-3">
                      <Link to={`/coordinacion/encuentros/${enc.id}`} className="text-primary-600 hover:text-primary-800 font-medium">Ver</Link>
                    </td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay encuentros registrados.</td>
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
                <button onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) - 1 })} disabled={(filters.page ?? 1) <= 1} className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50">Anterior</button>
                <button onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) + 1 })} disabled={(filters.page ?? 1) * (filters.limit ?? 20) >= data.total} className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50">Siguiente</button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
