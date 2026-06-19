import { useState } from 'react'
import { isAxiosError } from 'axios'
import { Card } from '@/shared/components/Card'
import { Toast } from '@/shared/components/Toast'
import { useSession } from '@/shared/hooks/useSession'
import { ApiError } from '@/shared/types/api'
import { useComunicaciones } from '@/features/comunicaciones/hooks/useComunicaciones'
import { EnvioForm, type EnvioFormValues } from '@/features/comunicaciones/components/EnvioForm'
import { ComunicacionPreview } from '@/features/comunicaciones/components/ComunicacionPreview'
import { LotesPanel } from '@/features/comunicaciones/components/LotesPanel'
import { LoteDetalle } from '@/features/comunicaciones/components/LoteDetalle'
import { ConfirmDialog } from '@/features/comunicaciones/components/ConfirmDialog'
import type { PreviewResponse } from '@/features/comunicaciones/types/comunicaciones'

function mensajeError(error: unknown, fallback: string): string {
  if (error instanceof ApiError) return error.message || fallback
  if (isAxiosError<{ detail?: string }>(error)) return error.response?.data?.detail ?? fallback
  return fallback
}

export default function ComunicacionesPage() {
  const { hasPermission } = useSession()
  const canAprobar = hasPermission('comunicacion:aprobar')

  const {
    lotesQuery,
    previewMutation,
    enviarMutation,
    aprobarMutation,
    cancelarLoteMutation,
    cancelarComunicacionMutation,
  } = useComunicaciones()

  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)
  const [preview, setPreview] = useState<PreviewResponse | null>(null)
  const [selectedLoteId, setSelectedLoteId] = useState<string | null>(null)
  const [accionLoteId, setAccionLoteId] = useState<string | null>(null)
  const [loteACancelar, setLoteACancelar] = useState<string | null>(null)

  const notify = (message: string, variant: 'success' | 'error') => setToast({ message, variant })

  const handlePreview = async (values: EnvioFormValues) => {
    setPreview(null)
    try {
      const result = await previewMutation.mutateAsync({ asunto: values.asunto, cuerpo: values.cuerpo })
      setPreview(result)
    } catch (error) {
      notify(mensajeError(error, 'No se pudo generar la previsualización.'), 'error')
    }
  }

  const handleSend = async (values: EnvioFormValues) => {
    try {
      const result = await enviarMutation.mutateAsync({
        materia_id: values.materiaId,
        asunto: values.asunto,
        cuerpo: values.cuerpo,
      })
      if (result.mensajes_creados === 0) {
        notify('No hay alumnos atrasados en la materia: no se encoló ninguna comunicación.', 'success')
      } else {
        notify(`Se encolaron ${result.mensajes_creados} comunicaciones en estado Pendiente.`, 'success')
        setSelectedLoteId(result.lote_id)
      }
    } catch (error) {
      notify(mensajeError(error, 'No se pudo encolar la comunicación.'), 'error')
    }
  }

  const handleAprobar = async (loteId: string) => {
    setAccionLoteId(loteId)
    try {
      const result = await aprobarMutation.mutateAsync(loteId)
      notify(`Lote aprobado: ${result.afectados} comunicaciones pasaron a Enviando.`, 'success')
    } catch (error) {
      notify(mensajeError(error, 'No se pudo aprobar el lote.'), 'error')
    } finally {
      setAccionLoteId(null)
    }
  }

  const confirmarCancelarLote = async () => {
    if (!loteACancelar) return
    const loteId = loteACancelar
    setAccionLoteId(loteId)
    try {
      const result = await cancelarLoteMutation.mutateAsync(loteId)
      notify(`Lote cancelado: ${result.afectados} comunicaciones canceladas.`, 'success')
    } catch (error) {
      notify(mensajeError(error, 'No se pudo cancelar el lote.'), 'error')
    } finally {
      setAccionLoteId(null)
      setLoteACancelar(null)
    }
  }

  const handleCancelarComunicacion = async (comunicacionId: string) => {
    try {
      await cancelarComunicacionMutation.mutateAsync(comunicacionId)
      notify('Comunicación cancelada.', 'success')
    } catch (error) {
      notify(mensajeError(error, 'No se pudo cancelar la comunicación.'), 'error')
    }
  }

  return (
    <div className="space-y-6">
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <h1 className="text-2xl font-bold text-gray-900">Comunicaciones</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <EnvioForm
            onPreview={handlePreview}
            onSend={handleSend}
            isLoadingPreview={previewMutation.isPending}
            isLoadingSend={enviarMutation.isPending}
            canSend={preview !== null}
          />
        </Card>

        {preview && (
          <Card className="p-6">
            <ComunicacionPreview asunto={preview.asunto_renderizado} cuerpo={preview.cuerpo_renderizado} />
          </Card>
        )}
      </div>

      <Card>
        <div className="border-b p-4">
          <h2 className="text-lg font-semibold text-gray-900">Lotes de comunicaciones</h2>
          <p className="text-sm text-gray-600">
            Seguimiento de estados por lote.
            {!canAprobar && ' La aprobación requiere el permiso de aprobación de comunicaciones.'}
          </p>
        </div>
        <LotesPanel
          lotes={lotesQuery.data?.items}
          isLoading={lotesQuery.isLoading}
          isError={lotesQuery.isError}
          canAprobar={canAprobar}
          selectedLoteId={selectedLoteId}
          accionLoteId={accionLoteId}
          onVerDetalle={(loteId) => setSelectedLoteId((current) => (current === loteId ? null : loteId))}
          onAprobar={handleAprobar}
          onCancelar={(loteId) => setLoteACancelar(loteId)}
        />
        {selectedLoteId && (
          <div className="border-t p-4">
            <LoteDetalle
              loteId={selectedLoteId}
              canAprobar={canAprobar}
              cancelandoId={cancelarComunicacionMutation.isPending ? cancelarComunicacionMutation.variables ?? null : null}
              onCancelarComunicacion={handleCancelarComunicacion}
            />
          </div>
        )}
      </Card>

      <ConfirmDialog
        open={loteACancelar !== null}
        titulo="Cancelar lote de comunicaciones"
        mensaje="Se cancelarán todas las comunicaciones Pendientes del lote. Las ya enviadas no se modifican. Esta acción no se puede deshacer."
        confirmLabel="Cancelar lote"
        isLoading={cancelarLoteMutation.isPending}
        onConfirm={confirmarCancelarLote}
        onCancel={() => setLoteACancelar(null)}
      />
    </div>
  )
}
