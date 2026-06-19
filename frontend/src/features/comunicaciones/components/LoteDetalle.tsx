import { useLoteDetalle } from '@/features/comunicaciones/hooks/useLoteDetalle'
import { EstadoBadge } from '@/features/comunicaciones/components/EstadoBadge'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'

interface LoteDetalleProps {
  loteId: string
  canAprobar: boolean
  cancelandoId: string | null
  onCancelarComunicacion: (comunicacionId: string) => void
}

export function LoteDetalle({ loteId, canAprobar, cancelandoId, onCancelarComunicacion }: LoteDetalleProps) {
  const { data, isLoading, isError } = useLoteDetalle(loteId)

  if (isLoading) return <Spinner size="sm" />
  if (isError) return <p className="text-sm text-red-700">No se pudo cargar el detalle del lote.</p>
  if (!data || data.comunicaciones.length === 0) {
    return <p className="text-sm text-gray-500">El lote no tiene comunicaciones.</p>
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Destinatarios del lote</p>
      {data.comunicaciones.map((c) => (
        <div key={c.id} className="flex items-center justify-between gap-3 rounded-lg border border-gray-100 p-2">
          <p className="truncate text-sm text-gray-900">{c.destinatario}</p>
          <div className="flex shrink-0 items-center gap-2">
            <EstadoBadge estado={c.estado} />
            {canAprobar && c.estado === 'Pendiente' && (
              <Button
                variant="ghost"
                size="sm"
                type="button"
                aria-label={`Cancelar comunicación a ${c.destinatario}`}
                loading={cancelandoId === c.id}
                onClick={() => onCancelarComunicacion(c.id)}
              >
                Cancelar
              </Button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
