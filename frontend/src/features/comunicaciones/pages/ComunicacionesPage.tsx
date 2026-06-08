import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Alert } from '@/shared/components/Alert'
import { usePreview } from '@/features/comunicaciones/hooks/usePreview'
import { useEnviar } from '@/features/comunicaciones/hooks/useEnviar'
import { ComunicacionPreview } from '@/features/comunicaciones/components/ComunicacionPreview'
import { EnvioForm } from '@/features/comunicaciones/components/EnvioForm'
import { TrackingTimeline } from '@/features/comunicaciones/components/TrackingTimeline'

interface FormValues {
  comisionId: string
  tipo: string
  asunto: string
  cuerpo: string
  destinatarios: string
}

export default function ComunicacionesPage() {
  const previewMutation = usePreview()
  const enviarMutation = useEnviar()
  const [preview, setPreview] = useState<{ asunto: string; cuerpo: string; destinatarios_count: number } | null>(null)
  const [envioId, setEnvioId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handlePreview = async (values: FormValues) => {
    setError(null)
    setPreview(null)
    try {
      const result = await previewMutation.mutateAsync({
        tipo: values.tipo,
        destinatarios: values.destinatarios.split(',').map((s) => s.trim()),
        template: values.cuerpo,
      })
      setPreview(result)
    } catch {
      setError('Error al generar la previsualización')
    }
  }

  const handleSend = async (values: FormValues) => {
    setError(null)
    try {
      const result = await enviarMutation.mutateAsync({
        comision_id: values.comisionId,
        tipo: values.tipo,
        asunto: values.asunto,
        cuerpo: values.cuerpo,
        destinatarios: values.destinatarios.split(',').map((s) => s.trim()),
      })
      setEnvioId(result.envio_id)
    } catch {
      setError('Error al enviar la comunicación')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Comunicaciones</h1>

      {error && <Alert variant="error">{error}</Alert>}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <EnvioForm
            onPreview={handlePreview}
            onSend={handleSend}
            isLoadingPreview={previewMutation.isPending}
            isLoadingSend={enviarMutation.isPending}
          />
        </Card>

        <div className="space-y-6">
          {preview && (
            <Card className="p-6">
              <ComunicacionPreview asunto={preview.asunto} cuerpo={preview.cuerpo} destinatariosCount={preview.destinatarios_count} />
            </Card>
          )}

          {envioId && (
            <Card className="p-6">
              <h2 className="mb-4 text-lg font-semibold">Seguimiento</h2>
              <TrackingTimeline envioId={envioId} />
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
