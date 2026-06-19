import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import {
  useFacturas,
  useCrearFactura,
  useMarcarAbonada,
  useEliminarFactura,
} from '@/features/liquidaciones/hooks/useLiquidaciones'
import { FacturaTable } from '@/features/liquidaciones/components/FacturaTable'
import { FacturaForm } from '@/features/liquidaciones/components/FacturaForm'
import type { FacturaFilters, FacturaCreate, EstadoFactura } from '@/features/liquidaciones/types'

export default function FacturasPage() {
  const [filters, setFilters] = useState<FacturaFilters>({})
  const [showForm, setShowForm] = useState(false)

  const { data, isLoading } = useFacturas(filters)
  const crearFactura = useCrearFactura()
  const marcarAbonada = useMarcarAbonada()
  const eliminarFactura = useEliminarFactura()

  const handleSave = async (payload: FacturaCreate) => {
    await crearFactura.mutateAsync(payload)
    setShowForm(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Facturas Docentes</h1>
        <Button onClick={() => setShowForm(true)}>Nueva factura</Button>
      </div>

      {showForm && (
        <Card className="p-6">
          <h3 className="mb-4 text-lg font-semibold">Nueva Factura</h3>
          <FacturaForm
            onSave={handleSave}
            onCancel={() => setShowForm(false)}
          />
        </Card>
      )}

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
            <label className="block text-xs font-medium text-gray-600">Estado</label>
            <select
              value={filters.estado ?? ''}
              onChange={(e) => setFilters({ ...filters, estado: (e.target.value as EstadoFactura) || undefined })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="Pendiente">Pendiente</option>
              <option value="Abonada">Abonada</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Desde</label>
            <input
              type="date"
              value={filters.desde ?? ''}
              onChange={(e) => setFilters({ ...filters, desde: e.target.value || undefined })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Hasta</label>
            <input
              type="date"
              value={filters.hasta ?? ''}
              onChange={(e) => setFilters({ ...filters, hasta: e.target.value || undefined })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <FacturaTable
          facturas={data ?? []}
          onMarcarAbonada={(id) => marcarAbonada.mutate(id)}
          onEliminar={(id) => eliminarFactura.mutate(id)}
          loading={marcarAbonada.isPending}
        />
      )}
    </div>
  )
}
