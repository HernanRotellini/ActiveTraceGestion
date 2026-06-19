interface AckProgressBarProps {
  total_acks: number
  sin_confirmar: number
}

export function AckProgressBar({ total_acks, sin_confirmar }: AckProgressBarProps) {
  const total = total_acks + sin_confirmar
  const porcentaje = total > 0 ? Math.round((total_acks / total) * 100) : 0

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Confirmaciones de lectura</span>
        <span className="font-medium text-gray-900">{total_acks}/{total} ({porcentaje}%)</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-primary-600 transition-all duration-500"
          style={{ width: `${porcentaje}%` }}
        />
      </div>
    </div>
  )
}
