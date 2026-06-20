import { useState } from 'react'
import { useCohortesList } from '@/features/admin/hooks/useAdmin'
import { LiquidacionKPIs } from '@/features/liquidaciones/components/LiquidacionKPIs'
import { useCerrarLiquidacion, usePreviewLiquidacion } from '@/features/liquidaciones/hooks/useLiquidaciones'
import type { LiquidacionPreviewResponse } from '@/features/liquidaciones/types'
import { Alert } from '@/shared/components/Alert'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { Spinner } from '@/shared/components/Spinner'
import { useSession } from '@/shared/hooks/useSession'
import { ApiError } from '@/shared/types/api'

export default function LiquidacionPeriodoPage() {
  const { hasPermission } = useSession()
  const [cohorteId, setCohorteId] = useState('')
  const [periodo, setPeriodo] = useState('')
  const [preview, setPreview] = useState<LiquidacionPreviewResponse | null>(null)
  const [confirmCierre, setConfirmCierre] = useState(false)
  const [error, setError] = useState('')

  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortesList()
  const previewMutation = usePreviewLiquidacion()
  const cerrar = useCerrarLiquidacion()

  const puedeGestionar = hasPermission('liquidaciones:calcular_cerrar')
  const cohorteItems = (cohortesResp?.items ?? [])
    .map((cohorte) => ({
      value: cohorte.id,
      label: `${cohorte.nombre} (${cohorte.anio})`,
    }))
    .sort((a, b) => a.label.localeCompare(b.label))

  const handlePreview = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!cohorteId || !periodo.trim()) {
      setError('Cohorte y periodo son obligatorios.')
      return
    }
    if (!/^\d{4}-\d{2}$/.test(periodo.trim())) {
      setError('El periodo debe tener formato YYYY-MM (ej: 2026-06).')
      return
    }
    try {
      const result = await previewMutation.mutateAsync({
        cohorte_id: cohorteId,
        periodo: periodo.trim(),
      })
      setPreview(result)
      setConfirmCierre(false)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error al generar el preview de liquidacion.')
    }
  }

  const handleCerrar = async () => {
    if (!cohorteId || !periodo.trim()) return
    try {
      await cerrar.mutateAsync({ cohorte_id: cohorteId, periodo: periodo.trim() })
      setConfirmCierre(false)
      setPreview(null)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error al cerrar la liquidacion.')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Liquidacion del Periodo</h1>

      <Card className="p-6">
        <form onSubmit={handlePreview} className="space-y-4">
          {error && <Alert variant="error">{error}</Alert>}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Combobox
              label="Cohorte *"
              items={cohorteItems}
              value={cohorteId}
              onChange={setCohorteId}
              placeholder="Seleccionar cohorte"
              searchPlaceholder="Buscar cohorte..."
              noResultsText="No hay cohortes disponibles."
              isLoading={loadingCohortes}
            />
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">Periodo * (YYYY-MM)</label>
              <input
                type="month"
                value={periodo}
                onChange={(e) => setPeriodo(e.target.value)}
                placeholder="ej: 2026-06"
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
          </div>
          <div className="flex justify-end">
            <Button type="submit" loading={previewMutation.isPending}>
              Generar preview
            </Button>
          </div>
        </form>
      </Card>

      {preview && (
        <>
          <LiquidacionKPIs
            totalPagable={preview.total_pagable}
            segmentoNexo={preview.segmento_nexo_total}
            segmentoFacturantes={preview.segmento_facturantes_total}
            totalItems={preview.items.length}
          />

          <div className="overflow-x-auto rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Usuario</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-600">Rol</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Base</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Plus</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-600">Total</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-600">NEXO</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-600">Procesable</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {preview.items.map((item, idx) => (
                  <tr key={idx} className={`hover:bg-gray-50 ${!item.procesable ? 'opacity-50' : ''}`}>
                    <td className="px-4 py-3 font-mono text-xs text-gray-600">{item.usuario_id}</td>
                    <td className="px-4 py-3 text-gray-600">{item.rol}</td>
                    <td className="px-4 py-3 text-right">${Number(item.monto_base).toLocaleString()}</td>
                    <td className="px-4 py-3 text-right">${Number(item.monto_plus).toLocaleString()}</td>
                    <td className="px-4 py-3 text-right font-medium">${Number(item.monto_total).toLocaleString()}</td>
                    <td className="px-4 py-3 text-center">
                      {item.es_nexo && (
                        <span className="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                          NEXO
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {item.procesable ? (
                        <span className="inline-flex rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                          Si
                        </span>
                      ) : (
                        <span
                          className="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700"
                          title={item.motivo_no_procesable ?? ''}
                        >
                          No
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {puedeGestionar && (
            <div className="flex justify-end">
              {confirmCierre ? (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Confirmar cierre de liquidacion?</span>
                  <Button variant="danger" onClick={handleCerrar} loading={cerrar.isPending}>
                    Confirmar cierre
                  </Button>
                  <Button variant="secondary" onClick={() => setConfirmCierre(false)}>
                    Cancelar
                  </Button>
                </div>
              ) : (
                <Button onClick={() => setConfirmCierre(true)}>Cerrar liquidacion</Button>
              )}
            </div>
          )}
        </>
      )}

      {!preview && !previewMutation.isPending && (
        <Card className="p-12 text-center">
          <p className="text-gray-500">Selecciona la cohorte y el periodo para generar un preview.</p>
        </Card>
      )}

      {previewMutation.isPending && (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      )}
    </div>
  )
}
