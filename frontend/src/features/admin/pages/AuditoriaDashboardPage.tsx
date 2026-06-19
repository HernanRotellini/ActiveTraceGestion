import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { AuditoriaFiltros } from '@/features/admin/components/AuditoriaFiltros'
import { useAccionesPorDia, useComunicacionesPorDocente, useInteracciones, useUltimasAcciones } from '@/features/admin/hooks/useAdmin'

function MiniBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? (value / max) * 100 : 0
  return (
    <div className="h-2 w-full rounded-full bg-gray-200">
      <div className="h-2 rounded-full bg-primary-500 transition-all" style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function AuditoriaDashboardPage() {
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [accion, setAccion] = useState('')

  const panelFilters = {
    fecha_desde: fechaDesde || undefined,
    fecha_hasta: fechaHasta || undefined,
  }

  const { data: accionesData, isLoading: loadingAcciones } = useAccionesPorDia(panelFilters)
  const { data: comunicacionesData, isLoading: loadingComs } = useComunicacionesPorDocente(panelFilters)
  const { data: interaccionesData, isLoading: loadingInter } = useInteracciones(panelFilters)
  const { data: ultimasData, isLoading: loadingUltimas } = useUltimasAcciones({ max_results: 10 })

  const isLoading = loadingAcciones || loadingComs || loadingInter

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Panel de Auditoría</h1>

      <AuditoriaFiltros
        accion={accion}
        fechaDesde={fechaDesde}
        fechaHasta={fechaHasta}
        onAccionChange={setAccion}
        onFechaDesdeChange={setFechaDesde}
        onFechaHastaChange={setFechaHasta}
      />

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Acciones registradas</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">
                {accionesData?.items?.reduce((acc, d) => acc + d.total, 0) ?? 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Últimas acciones (hoy)</p>
              <p className="mt-1 text-2xl font-bold text-primary-600">
                {accionesData?.items?.slice(-1)[0]?.total ?? 0}
              </p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Interacciones</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">
                {interaccionesData?.items?.length ?? 0}
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Acciones por día</h3>
              <div className="space-y-3">
                {accionesData?.items?.map((d) => {
                  const maxAcciones = Math.max(...(accionesData.items?.map((a) => a.total) ?? [0]), 1)
                  return (
                    <div key={d.fecha} className="flex items-center gap-3 text-sm">
                      <span className="w-24 text-gray-600">{new Date(d.fecha).toLocaleDateString()}</span>
                      <div className="flex-1">
                        <MiniBar value={d.total} max={maxAcciones} />
                      </div>
                      <span className="w-12 text-right font-medium text-gray-900">{d.total}</span>
                    </div>
                  )
                })}
                {(!accionesData?.items || accionesData.items.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Comunicaciones por docente</h3>
              <div className="space-y-3">
                {comunicacionesData?.items?.map((c, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="font-mono text-xs text-gray-500">{c.docente_id}</span>
                    </div>
                    <div className="flex gap-3">
                      <span className="text-gray-600">{c.accion}</span>
                      <span className="font-medium text-gray-900">{c.total}</span>
                    </div>
                  </div>
                ))}
                {(!comunicacionesData?.items || comunicacionesData.items.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Interacciones por docente/materia</h3>
              <div className="space-y-2">
                {interaccionesData?.items?.slice(0, 10).map((i, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="font-mono text-xs text-gray-500">{i.docente_id}</span>
                      {i.materia_id && <span className="ml-2 text-gray-400 text-xs">· {i.materia_id}</span>}
                    </div>
                    <div className="flex gap-2">
                      <span className="text-gray-600">{i.accion}</span>
                      <span className="font-medium text-gray-900">{i.total}</span>
                    </div>
                  </div>
                ))}
                {(!interaccionesData?.items || interaccionesData.items.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Últimas acciones</h3>
              {loadingUltimas ? <Spinner /> : (
                <div className="space-y-2 max-h-80 overflow-y-auto">
                  {ultimasData?.items?.map((entry) => (
                    <div key={entry.id} className="border-b border-gray-100 pb-2 text-sm last:border-0">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-xs text-gray-500">{entry.actor_id}</span>
                        <span className="text-xs text-gray-400">{new Date(entry.fecha_hora).toLocaleString()}</span>
                      </div>
                      <p className="text-gray-600">{entry.accion}</p>
                    </div>
                  ))}
                  {(!ultimasData?.items || ultimasData.items.length === 0) && (
                    <p className="text-sm text-gray-500">Sin acciones recientes.</p>
                  )}
                </div>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
