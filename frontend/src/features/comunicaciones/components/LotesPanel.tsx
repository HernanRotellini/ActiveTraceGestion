import { useQuery } from '@tanstack/react-query'
import { Button } from '@/shared/components/Button'
import { Spinner } from '@/shared/components/Spinner'
import { fetchMaterias } from '@/features/comunicaciones/services/comunicaciones'
import type { LoteResumen, MateriaOption } from '@/features/comunicaciones/types/comunicaciones'

interface LotesPanelProps {
  lotes?: LoteResumen[]
  isLoading: boolean
  isError: boolean
  canAprobar: boolean
  selectedLoteId: string | null
  accionLoteId: string | null
  onVerDetalle: (loteId: string) => void
  onAprobar: (loteId: string) => void
  onCancelar: (loteId: string) => void
}

function Conteo({ label, valor, color }: { label: string; valor: number; color: string }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {label}: {valor}
    </span>
  )
}

export function LotesPanel({
  lotes,
  isLoading,
  isError,
  canAprobar,
  selectedLoteId,
  accionLoteId,
  onVerDetalle,
  onAprobar,
  onCancelar,
}: LotesPanelProps) {
  const { data: materias = [] } = useQuery({
    queryKey: ['materias-comunicaciones'],
    queryFn: fetchMaterias,
    staleTime: 60_000,
  })
  const materiaPorId = new Map(materias.map((m: MateriaOption) => [m.id, m.nombre]))

  if (isLoading) {
    return (
      <div className="flex justify-center py-10">
        <Spinner />
      </div>
    )
  }

  if (isError) {
    return <p className="py-8 text-center text-red-700">No se pudieron cargar los lotes de comunicaciones.</p>
  }

  if (!lotes || lotes.length === 0) {
    return <p className="py-8 text-center text-gray-500">Todavía no se encoló ninguna comunicación.</p>
  }

  return (
    <ul className="divide-y divide-gray-100">
      {lotes.map((lote) => {
        const enAccion = accionLoteId === lote.lote_id
        const hayPendientes = lote.pendientes > 0
        return (
          <li
            key={lote.lote_id}
            className={`space-y-3 p-4 ${selectedLoteId === lote.lote_id ? 'bg-primary-50/40' : ''}`}
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {materiaPorId.get(lote.materia_id) ?? 'Materia'}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(lote.created_at).toLocaleString()} · {lote.total} destinatarios
                </p>
              </div>
              <div className="flex flex-wrap gap-1.5">
                <Conteo label="Pend." valor={lote.pendientes} color="bg-yellow-100 text-yellow-700" />
                <Conteo label="Env." valor={lote.enviados} color="bg-green-100 text-green-700" />
                <Conteo label="Error" valor={lote.errores} color="bg-red-100 text-red-700" />
                <Conteo label="Canc." valor={lote.cancelados} color="bg-gray-100 text-gray-700" />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button variant="ghost" size="sm" type="button" onClick={() => onVerDetalle(lote.lote_id)}>
                Ver detalle
              </Button>
              {canAprobar && (
                <>
                  <Button
                    size="sm"
                    type="button"
                    onClick={() => onAprobar(lote.lote_id)}
                    loading={enAccion}
                    disabled={!hayPendientes}
                  >
                    Aprobar
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    type="button"
                    onClick={() => onCancelar(lote.lote_id)}
                    disabled={enAccion || !hayPendientes}
                  >
                    Cancelar
                  </Button>
                </>
              )}
            </div>
          </li>
        )
      })}
    </ul>
  )
}
