interface ComunicacionPreviewProps {
  asunto: string
  cuerpo: string
  destinatariosCount: number
}

export function ComunicacionPreview({ asunto, cuerpo, destinatariosCount }: ComunicacionPreviewProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Previsualización</h2>

      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Asunto</p>
        <p className="mt-1 text-sm font-medium text-gray-900">{asunto}</p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Cuerpo</p>
        <p className="mt-1 whitespace-pre-wrap text-sm text-gray-700">{cuerpo}</p>
      </div>

      <p className="text-sm text-gray-500">
        Se enviará a <span className="font-medium">{destinatariosCount}</span> destinatarios.
      </p>
    </div>
  )
}
