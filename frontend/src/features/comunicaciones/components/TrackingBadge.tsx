import type { EstadoComunicacion } from '@/features/comunicaciones/types/comunicaciones'

interface TrackingBadgeProps {
  estado: EstadoComunicacion
}

const colorMap: Record<EstadoComunicacion, string> = {
  pendiente: 'bg-yellow-100 text-yellow-700',
  enviado: 'bg-green-100 text-green-700',
  fallido: 'bg-red-100 text-red-700',
  cancelado: 'bg-gray-100 text-gray-700',
}

const labelMap: Record<EstadoComunicacion, string> = {
  pendiente: 'Pendiente',
  enviado: 'Enviado',
  fallido: 'Fallido',
  cancelado: 'Cancelado',
}

export function TrackingBadge({ estado }: TrackingBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${colorMap[estado]}`}
    >
      {labelMap[estado]}
    </span>
  )
}
