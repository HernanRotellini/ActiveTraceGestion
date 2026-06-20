import { useState } from 'react'
import { useCohortesList } from '@/features/admin/hooks/useAdmin'
import { LiquidacionTable } from '@/features/liquidaciones/components/LiquidacionTable'
import { useLiquidaciones } from '@/features/liquidaciones/hooks/useLiquidaciones'
import type { LiquidacionFilters, SegmentoLiquidacion } from '@/features/liquidaciones/types'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { Spinner } from '@/shared/components/Spinner'

const SEGMENTOS: { label: string; value: SegmentoLiquidacion }[] = [
  { label: 'General', value: 'general' },
  { label: 'NEXO', value: 'nexo' },
  { label: 'Facturante', value: 'facturante' },
]

export default function LiquidacionHistorialPage() {
  const [filters, setFilters] = useState<LiquidacionFilters>({})
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortesList()
  const { data, isLoading } = useLiquidaciones(filters)
  const cohorteItems = (cohortesResp?.items ?? [])
    .map((cohorte) => ({
      value: cohorte.id,
      label: `${cohorte.nombre} (${cohorte.anio})`,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Historial de Liquidaciones</h1>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Periodo (YYYY-MM)</label>
            <input
              type="text"
              value={filters.periodo ?? ''}
              onChange={(e) => setFilters({ ...filters, periodo: e.target.value || undefined })}
              placeholder="ej: 2026-06"
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="w-64">
            <Combobox
              label="Cohorte"
              items={cohorteItems}
              value={filters.cohorte_id ?? ''}
              onChange={(value) => setFilters({ ...filters, cohorte_id: value || undefined })}
              placeholder="Todas las cohortes"
              searchPlaceholder="Buscar cohorte..."
              noResultsText="No hay cohortes disponibles."
              isLoading={loadingCohortes}
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Segmento</label>
            <select
              value={filters.segmento ?? ''}
              onChange={(e) => setFilters({ ...filters, segmento: (e.target.value as SegmentoLiquidacion) || undefined })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              {SEGMENTOS.map((segmento) => (
                <option key={segmento.value} value={segmento.value}>
                  {segmento.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <LiquidacionTable items={data ?? []} />
      )}
    </div>
  )
}
