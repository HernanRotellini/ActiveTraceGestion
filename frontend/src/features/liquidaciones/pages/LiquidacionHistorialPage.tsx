import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useLiquidaciones } from '@/features/liquidaciones/hooks/useLiquidaciones'
import { LiquidacionTable } from '@/features/liquidaciones/components/LiquidacionTable'
import type { LiquidacionFilters, SegmentoLiquidacion } from '@/features/liquidaciones/types'

const SEGMENTOS: { label: string; value: SegmentoLiquidacion }[] = [
  { label: 'General', value: 'general' },
  { label: 'NEXO', value: 'nexo' },
  { label: 'Facturante', value: 'facturante' },
]

export default function LiquidacionHistorialPage() {
  const [filters, setFilters] = useState<LiquidacionFilters>({})
  const { data, isLoading } = useLiquidaciones(filters)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Historial de Liquidaciones</h1>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Período (YYYY-MM)</label>
            <input
              type="text"
              value={filters.periodo ?? ''}
              onChange={(e) => setFilters({ ...filters, periodo: e.target.value || undefined })}
              placeholder="ej: 2026-06"
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Cohorte ID</label>
            <input
              type="text"
              value={filters.cohorte_id ?? ''}
              onChange={(e) => setFilters({ ...filters, cohorte_id: e.target.value || undefined })}
              placeholder="UUID cohorte"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
              {SEGMENTOS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <LiquidacionTable items={data ?? []} />
      )}
    </div>
  )
}
