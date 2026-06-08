import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useHistorial } from '@/features/liquidaciones/hooks/useLiquidaciones'
import type { LiquidacionFilters } from '@/features/liquidaciones/types'

export default function LiquidacionHistorialPage() {
  const [filters, setFilters] = useState<LiquidacionFilters>({ page: 1, limit: 20 })
  const { data, isLoading } = useHistorial(filters)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Historial de Liquidaciones</h1>
        <Link
          to="/liquidaciones"
          className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Período actual
        </Link>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <div className="space-y-4">
          {data?.items.map((liq) => (
            <Card key={liq.id} className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{liq.periodo}</h3>
                  <p className="text-sm text-gray-500">{liq.cohorte_nombre}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">${liq.total_general.toLocaleString()}</p>
                  <span className="inline-flex rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                    Cerrada
                  </span>
                </div>
              </div>
              <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                <span>Gral: ${liq.total_general.toLocaleString()}</span>
                <span>NEXO: ${liq.total_nexo.toLocaleString()}</span>
                <span>Factura: ${liq.total_factura.toLocaleString()}</span>
                {liq.cerrada_en && <span>Cerrada: {new Date(liq.cerrada_en).toLocaleDateString()}</span>}
              </div>
            </Card>
          ))}
          {(!data?.items || data.items.length === 0) && (
            <Card className="p-12 text-center">
              <p className="text-gray-500">No hay liquidaciones cerradas.</p>
            </Card>
          )}
        </div>
      )}

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
    </div>
  )
}
