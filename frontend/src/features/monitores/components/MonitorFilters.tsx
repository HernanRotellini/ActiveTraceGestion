import { Combobox } from '@/shared/components/Combobox'
import { useMaterias } from '@/features/admin/hooks/useAdmin'
import type { MonitorFilters as MonitorFiltersType } from '@/features/monitores/types/monitores'

interface MonitorFiltersProps {
  filters: MonitorFiltersType
  onChange: (filters: MonitorFiltersType) => void
}

export function MonitorFilters({ filters, onChange }: MonitorFiltersProps) {
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias()
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({
    value: m.id,
    label: `${m.nombre} (${m.codigo})${m.carrera_nombre ? ` - ${m.carrera_nombre}` : ''}`,
  }))

  const update = <K extends keyof MonitorFiltersType>(key: K, value: MonitorFiltersType[K] | '') => {
    onChange({ ...filters, [key]: value || undefined })
  }

  return (
    <div className="flex flex-wrap gap-4">
      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Búsqueda (alumno o email)</label>
        <input
          type="text"
          value={filters.busqueda ?? ''}
          onChange={(e) => update('busqueda', e.target.value)}
          placeholder="Nombre o email..."
          className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="w-52">
        <Combobox
          label="Materia"
          items={materiaItems}
          value={filters.materia_id ?? ''}
          onChange={(val) => update('materia_id', val || undefined)}
          placeholder="Buscar materia..."
          isLoading={loadingMaterias}
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Comisión</label>
        <input
          type="text"
          value={filters.comision ?? ''}
          onChange={(e) => update('comision', e.target.value)}
          placeholder="Ej: A, Turno noche..."
          className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Regional</label>
        <input
          type="text"
          value={filters.regional ?? ''}
          onChange={(e) => update('regional', e.target.value)}
          placeholder="Regional..."
          className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Actividad</label>
        <input
          type="text"
          value={filters.actividad ?? ''}
          onChange={(e) => update('actividad', e.target.value)}
          placeholder="Nombre de actividad..."
          className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      <div className="space-y-1">
        <label className="block text-xs font-medium text-gray-600">Mín. actividades cumplidas</label>
        <input
          type="number"
          min={0}
          value={filters.min_actividad_cumplida ?? ''}
          onChange={(e) => update('min_actividad_cumplida', e.target.value ? Number(e.target.value) : undefined)}
          placeholder="0"
          className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>
  )
}
