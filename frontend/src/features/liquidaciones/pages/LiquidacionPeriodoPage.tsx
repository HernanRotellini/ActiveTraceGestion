import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { Alert } from '@/shared/components/Alert'
import { useSession } from '@/shared/hooks/useSession'
import { useLiquidacionActiva, useCerrarLiquidacion } from '@/features/liquidaciones/hooks/useLiquidaciones'
import { LiquidacionTable } from '@/features/liquidaciones/components/LiquidacionTable'
import { LiquidacionKPIs } from '@/features/liquidaciones/components/LiquidacionKPIs'
import type { LiquidacionFilters } from '@/features/liquidaciones/types'

export default function LiquidacionPeriodoPage() {
  const { hasPermission } = useSession()
  const [filters, setFilters] = useState<LiquidacionFilters>({})
  const [confirmCierre, setConfirmCierre] = useState(false)
  const { data: liquidacion, isLoading, error } = useLiquidacionActiva(filters)
  const cerrar = useCerrarLiquidacion()

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner /></div>
  }

  if (error) {
    return <Alert variant="error">Error al cargar la liquidación del período.</Alert>
  }

  if (!liquidacion) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Liquidación del Período</h1>
        <Card className="p-12 text-center">
          <p className="text-gray-500">No hay una liquidación activa para el período actual.</p>
        </Card>
      </div>
    )
  }

  const handleCerrar = async () => {
    try {
      await cerrar.mutateAsync(liquidacion.id)
      setConfirmCierre(false)
    } catch {
      // error handled by mutation
    }
  }

  const puedeGestionar = hasPermission('liquidaciones:gestionar')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Liquidación del Período</h1>
          <p className="text-sm text-gray-500">{liquidacion.periodo} · {liquidacion.cohorte_nombre}</p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/liquidaciones/historial"
            className="rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Historial
          </Link>
          {liquidacion.estado === 'abierta' && puedeGestionar && (
            <>
              {confirmCierre ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">¿Cerrar liquidación?</span>
                  <Button variant="danger" onClick={handleCerrar} loading={cerrar.isPending}>
                    Confirmar
                  </Button>
                  <Button variant="secondary" onClick={() => setConfirmCierre(false)}>
                    Cancelar
                  </Button>
                </div>
              ) : (
                <Button variant="primary" onClick={() => setConfirmCierre(true)}>
                  Cerrar liquidación
                </Button>
              )}
            </>
          )}
        </div>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Mes</label>
            <input
              type="month"
              value={filters.mes ?? ''}
              onChange={(e) => setFilters({ ...filters, mes: e.target.value || undefined })}
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Cohorte</label>
            <input
              type="text"
              value={filters.cohorte_id ?? ''}
              onChange={(e) => setFilters({ ...filters, cohorte_id: e.target.value || undefined })}
              placeholder="ID de cohorte"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Docente</label>
            <input
              type="text"
              value={filters.docente ?? ''}
              onChange={(e) => setFilters({ ...filters, docente: e.target.value || undefined })}
              placeholder="Nombre del docente"
              className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      <LiquidacionKPIs
        totalGeneral={liquidacion.total_general}
        totalNexo={liquidacion.total_nexo}
        totalFactura={liquidacion.total_factura}
        estado={liquidacion.estado}
      />

      <div className="space-y-6">
        <LiquidacionTable
          items={liquidacion.items}
          segmento="general"
          titulo="General"
          subtotal={liquidacion.total_general}
        />
        <LiquidacionTable
          items={liquidacion.items}
          segmento="nexo"
          titulo="NEXO"
          subtotal={liquidacion.total_nexo}
        />
        <LiquidacionTable
          items={liquidacion.items}
          segmento="factura"
          titulo="Factura"
          subtotal={liquidacion.total_factura}
        />
      </div>
    </div>
  )
}
