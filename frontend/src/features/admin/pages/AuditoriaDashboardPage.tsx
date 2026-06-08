import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { AuditoriaFiltros } from '@/features/admin/components/AuditoriaFiltros'
import { useMetricas } from '@/features/admin/hooks/useAdmin'
import { useLogAuditoria } from '@/features/admin/hooks/useAdmin'

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
  const [materia, setMateria] = useState('')
  const [usuario, setUsuario] = useState('')
  const [accion, setAccion] = useState('')

  const { data: metricas, isLoading } = useMetricas(
    { fecha_desde: fechaDesde || undefined, fecha_hasta: fechaHasta || undefined, materia: materia || undefined },
  )

  const { data: logData } = useLogAuditoria({
    usuario: usuario || undefined,
    materia: materia || undefined,
    accion: accion || undefined,
    fecha_desde: fechaDesde || undefined,
    fecha_hasta: fechaHasta || undefined,
    page: 1,
    limit: 200,
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Panel de Auditoría</h1>

      <AuditoriaFiltros
        usuario={usuario}
        materia={materia}
        accion={accion}
        fechaDesde={fechaDesde}
        fechaHasta={fechaHasta}
        onUsuarioChange={setUsuario}
        onMateriaChange={setMateria}
        onAccionChange={setAccion}
        onFechaDesdeChange={setFechaDesde}
        onFechaHastaChange={setFechaHasta}
      />

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : !metricas ? (
        <Card className="p-12 text-center">
          <p className="text-gray-500">No hay métricas disponibles.</p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Total Acciones</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{metricas.total_acciones}</p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Total Comunicaciones</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{metricas.total_comunicaciones}</p>
            </Card>
            <Card className="p-4">
              <p className="text-xs font-medium text-gray-500">Acciones (hoy)</p>
              <p className="mt-1 text-2xl font-bold text-primary-600">
                {metricas.acciones_por_dia?.slice(-1)[0]?.total ?? 0}
              </p>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Acciones por día</h3>
              <div className="space-y-3">
                {metricas.acciones_por_dia?.map((d) => {
                  const maxAcciones = Math.max(...(metricas.acciones_por_dia?.map((a) => a.total) ?? [0]), 1)
                  return (
                    <div key={d.fecha} className="flex items-center gap-3 text-sm">
                      <span className="w-24 text-gray-600">{d.fecha}</span>
                      <div className="flex-1">
                        <MiniBar value={d.total} max={maxAcciones} />
                      </div>
                      <span className="w-12 text-right font-medium text-gray-900">{d.total}</span>
                    </div>
                  )
                })}
                {(!metricas.acciones_por_dia || metricas.acciones_por_dia.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Estado de Comunicaciones</h3>
              <div className="space-y-3">
                {metricas.comunicaciones?.map((c) => (
                  <div key={c.docente_id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{c.docente_nombre}</span>
                    <div className="flex gap-3">
                      <span className="text-green-600">{c.enviadas} env.</span>
                      <span className="text-yellow-600">{c.pendientes} pend.</span>
                      <span className="text-red-600">{c.fallidas} fall.</span>
                    </div>
                  </div>
                ))}
                {(!metricas.comunicaciones || metricas.comunicaciones.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Interacciones por Docente/Materia</h3>
              <div className="space-y-2">
                {metricas.interacciones?.slice(0, 10).map((i) => (
                  <div key={`${i.docente_id}-${i.materia}`} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="text-gray-700">{i.docente_nombre}</span>
                      <span className="ml-2 text-gray-400">· {i.materia}</span>
                    </div>
                    <span className="font-medium text-gray-900">{i.total}</span>
                  </div>
                ))}
                {(!metricas.interacciones || metricas.interacciones.length === 0) && (
                  <p className="text-sm text-gray-500">Sin datos.</p>
                )}
              </div>
            </Card>

            <Card className="p-4">
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Últimas Acciones</h3>
              <div className="space-y-2 max-h-80 overflow-y-auto">
                {logData?.items?.slice(0, 10).map((entry) => (
                  <div key={entry.id} className="border-b border-gray-100 pb-2 text-sm last:border-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{entry.usuario}</span>
                      <span className="text-xs text-gray-400">{new Date(entry.fecha_hora).toLocaleString()}</span>
                    </div>
                    <p className="text-gray-600">{entry.accion}{entry.materia ? ` · ${entry.materia}` : ''}</p>
                  </div>
                ))}
                {(!logData?.items || logData.items.length === 0) && (
                  <p className="text-sm text-gray-500">Sin acciones recientes.</p>
                )}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
