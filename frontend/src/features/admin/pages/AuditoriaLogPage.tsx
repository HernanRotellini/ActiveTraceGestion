import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { AuditoriaFiltros } from '@/features/admin/components/AuditoriaFiltros'
import { useLogAuditoria } from '@/features/admin/hooks/useAdmin'
import type { AuditoriaFilters } from '@/features/admin/types'

const PAGE_SIZE = 20

export default function AuditoriaLogPage() {
  const [accion, setAccion] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [offset, setOffset] = useState(0)

  const filters: AuditoriaFilters = {
    accion: accion || undefined,
    fecha_desde: fechaDesde || undefined,
    fecha_hasta: fechaHasta || undefined,
    limit: PAGE_SIZE,
    offset,
  }

  const { data, isLoading } = useLogAuditoria(filters)

  const handleFilterChange = (updater: () => void) => {
    updater()
    setOffset(0)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Log de Auditoría</h1>

      <AuditoriaFiltros
        accion={accion}
        fechaDesde={fechaDesde}
        fechaHasta={fechaHasta}
        onAccionChange={(v) => handleFilterChange(() => setAccion(v))}
        onFechaDesdeChange={(v) => handleFilterChange(() => setFechaDesde(v))}
        onFechaHastaChange={(v) => handleFilterChange(() => setFechaHasta(v))}
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
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Actor</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Acción</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Filas</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">IP</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">User Agent</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data?.items?.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                      {new Date(entry.fecha_hora).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-gray-700">{entry.actor_id}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                        {entry.accion}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">{entry.filas_afectadas ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">{entry.ip ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs max-w-xs truncate">{entry.user_agent ?? '-'}</td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay entradas de auditoría.</td></tr>
                )}
              </tbody>
            </table>
          </Card>

          {data && data.total > PAGE_SIZE && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {offset + 1}–{Math.min(offset + PAGE_SIZE, data.total)} de {data.total}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  disabled={offset === 0}
                  className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                  disabled={offset + PAGE_SIZE >= data.total}
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
