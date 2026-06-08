import type { AckStatus } from '@/features/avisos/types'

interface AckProgressBarProps {
  acks: AckStatus[]
}

export function AckProgressBar({ acks }: AckProgressBarProps) {
  const total = acks.length
  const leidos = acks.filter((a) => a.leido).length
  const porcentaje = total > 0 ? Math.round((leidos / total) * 100) : 0

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">Lectura de aviso</span>
        <span className="font-medium text-gray-900">{leidos}/{total} ({porcentaje}%)</span>
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
