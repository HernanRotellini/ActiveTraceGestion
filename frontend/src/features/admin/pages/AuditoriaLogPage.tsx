import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { AuditoriaFiltros } from '@/features/admin/components/AuditoriaFiltros'
import { useLogAuditoria } from '@/features/admin/hooks/useAdmin'
import type { AuditoriaFilters } from '@/features/admin/types'

export default function AuditoriaLogPage() {
  const [filters, setFilters] = useState<AuditoriaFilters>({ page: 1, limit: 20 })

  const { data, isLoading } = useLogAuditoria(filters)

  const updateFilter = (key: keyof AuditoriaFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined, page: 1 }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Log de Auditoría</h1>
      </div>

      <AuditoriaFiltros
        usuario={filters.usuario ?? ''}
        materia={filters.materia ?? ''}
        accion={filters.accion ?? ''}
        fechaDesde={filters.fecha_desde ?? ''}
        fechaHasta={filters.fecha_hasta ?? ''}
        onUsuarioChange={(v) => updateFilter('usuario', v)}
        onMateriaChange={(v) => updateFilter('materia', v)}
        onAccionChange={(v) => updateFilter('accion', v)}
        onFechaDesdeChange={(v) => updateFilter('fecha_desde', v)}
        onFechaHastaChange={(v) => updateFilter('fecha_hasta', v)}
      />

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <>
          <Card className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Fecha/Hora</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Usuario</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Materia</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Acción</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Registros</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">IP</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">User Agent</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data?.items.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                      {new Date(entry.fecha_hora).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-medium text-gray-900">{entry.usuario}</td>
                    <td className="px-4 py-3 text-gray-600">{entry.materia ?? '-'}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                        {entry.accion}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">{entry.registros_afectados}</td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">{entry.ip_origen ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs max-w-xs truncate">{entry.user_agent ?? '-'}</td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-500">No hay entradas de auditoría.</td></tr>
                )}
              </tbody>
            </table>
          </Card>

          {data && data.total > (filters.limit ?? 20) && (
            <div className="flex items-center justify-between">
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
        </>
      )}
    </div>
  )
}
