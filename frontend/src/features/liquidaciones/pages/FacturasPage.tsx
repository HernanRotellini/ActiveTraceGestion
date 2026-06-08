import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { useFacturas, useCrearFactura, useCambiarEstadoFactura } from '@/features/liquidaciones/hooks/useLiquidaciones'
import { FacturaTable } from '@/features/liquidaciones/components/FacturaTable'
import { FacturaForm } from '@/features/liquidaciones/components/FacturaForm'
import type { FacturaFilters, FacturaPayload } from '@/features/liquidaciones/types'

export default function FacturasPage() {
  const [filters, setFilters] = useState<FacturaFilters>({ page: 1, limit: 20 })
  const [showForm, setShowForm] = useState(false)
  const { data, isLoading } = useFacturas(filters)
  const crearFactura = useCrearFactura()
  const cambiarEstado = useCambiarEstadoFactura()

  const handleSave = async (payload: FacturaPayload) => {
    await crearFactura.mutateAsync(payload)
    setShowForm(false)
  }

  const handleCambiarEstado = (id: string, estado: 'pendiente' | 'abonada') => {
    cambiarEstado.mutate({ id, estado })
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
            <label className="block text-xs font-medium text-gray-600">Docente</label>
            <input
              type="text"
              value={filters.docente ?? ''}
              onChange={(e) => setFilters({ ...filters, docente: e.target.value || undefined, page: 1 })}
              placeholder="Nombre del docente"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
              <option value="pendiente">Pendiente</option>
              <option value="abonada">Abonada</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Desde</label>
            <input
              type="date"
              value={filters.fecha_desde ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value || undefined, page: 1 })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Hasta</label>
            <input
              type="date"
              value={filters.fecha_hasta ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value || undefined, page: 1 })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <>
          <FacturaTable
            facturas={data?.items ?? []}
            onCambiarEstado={handleCambiarEstado}
            loading={cambiarEstado.isPending}
          />
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
