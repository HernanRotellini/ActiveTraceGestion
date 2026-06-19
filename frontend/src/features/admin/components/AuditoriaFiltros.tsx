import { Card } from '@/shared/components/Card'

interface AuditoriaFiltrosProps {
  accion?: string
  fechaDesde?: string
  fechaHasta?: string
  onAccionChange: (v: string) => void
  onFechaDesdeChange: (v: string) => void
  onFechaHastaChange: (v: string) => void
}

export function AuditoriaFiltros({
  accion, fechaDesde, fechaHasta,
  onAccionChange, onFechaDesdeChange, onFechaHastaChange,
}: AuditoriaFiltrosProps) {
  return (
    <Card className="p-4">
      <div className="flex flex-wrap gap-4">
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Acción</label>
          <input
            type="text"
            value={accion ?? ''}
            onChange={(e) => onAccionChange(e.target.value || '')}
            placeholder="ej: login, create, update"
            className="block w-48 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Desde</label>
          <input
            type="date"
            value={fechaDesde ?? ''}
            onChange={(e) => onFechaDesdeChange(e.target.value || '')}
            className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Hasta</label>
          <input
            type="date"
            value={fechaHasta ?? ''}
            onChange={(e) => onFechaHastaChange(e.target.value || '')}
            className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
    </Card>
  )
}
