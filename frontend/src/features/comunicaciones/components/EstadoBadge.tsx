import type { EstadoComunicacion } from '@/features/comunicaciones/types/comunicaciones'

interface EstadoBadgeProps {
  estado: EstadoComunicacion
}

const styleMap: Record<EstadoComunicacion, string> = {
  Pendiente: 'bg-yellow-100 text-yellow-700',
  Enviando: 'bg-blue-100 text-blue-700',
  Enviado: 'bg-green-100 text-green-700',
  Error: 'bg-red-100 text-red-700',
  Cancelado: 'bg-gray-100 text-gray-700',
}

export function EstadoBadge({ estado }: EstadoBadgeProps) {
  return (
    <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${styleMap[estado] ?? 'bg-gray-100 text-gray-700'}`}>
      {estado}
    </span>
  )
}
