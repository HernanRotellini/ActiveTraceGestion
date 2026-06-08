import type { MonitorFilters as MonitorFiltersType } from '@/features/monitores/types/monitores'

interface MonitorFiltersProps {
  filters: MonitorFiltersType
  onChange: (filters: MonitorFiltersType) => void
}

export function MonitorFilters({ filters, onChange }: MonitorFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4">
      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Comisión</label>
        <input
          type="text"
          value={filters.comision_id ?? ''}
          onChange={(e) => onChange({ ...filters, comision_id: e.target.value || undefined })}
          placeholder="ID de comisión"
          className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Materia</label>
        <input
          type="text"
          value={filters.materia_id ?? ''}
          onChange={(e) => onChange({ ...filters, materia_id: e.target.value || undefined })}
          placeholder="ID de materia"
          className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Estado</label>
        <select
          value={filters.estado ?? ''}
          onChange={(e) => onChange({ ...filters, estado: e.target.value || undefined })}
          className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">Todos</option>
          <option value="al_dia">Al día</option>
          <option value="atrasado">Atrasado</option>
          <option value="critico">Crítico</option>
        </select>
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Desde</label>
        <input
          type="date"
          value={filters.fecha_desde ?? ''}
          onChange={(e) => onChange({ ...filters, fecha_desde: e.target.value || undefined })}
          className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Hasta</label>
        <input
          type="date"
          value={filters.fecha_hasta ?? ''}
          onChange={(e) => onChange({ ...filters, fecha_hasta: e.target.value || undefined })}
          className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>
  )
}
