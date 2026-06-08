import { useTracking } from '@/features/comunicaciones/hooks/useTracking'
import { TrackingBadge } from '@/features/comunicaciones/components/TrackingBadge'
import { Spinner } from '@/shared/components/Spinner'

interface TrackingTimelineProps {
  envioId: string
}

export function TrackingTimeline({ envioId }: TrackingTimelineProps) {
  const { data, isLoading } = useTracking(envioId)

  if (isLoading) return <Spinner size="sm" />

  if (!data) {
    return <p className="text-sm text-gray-500">No hay datos de seguimiento.</p>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
        <div>
          <p className="text-sm font-medium text-gray-900">{data.asunto}</p>
          <p className="text-xs text-gray-500">
            {data.enviados} de {data.total} enviados
          </p>
        </div>
        <TrackingBadge estado={data.estado} />
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Destinatarios</p>
        {data.destinatarios.map((d, idx) => (
          <div
            key={`${d.email}-${idx}`}
            className="flex items-center justify-between rounded-lg border border-gray-100 p-2"
          >
            <div>
              <p className="text-sm text-gray-900">{d.nombre}</p>
              <p className="text-xs text-gray-500">{d.email}</p>
            </div>
            <div className="flex items-center gap-2">
              {d.error && <span className="text-xs text-red-500">{d.error}</span>}
              <TrackingBadge estado={d.estado} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
