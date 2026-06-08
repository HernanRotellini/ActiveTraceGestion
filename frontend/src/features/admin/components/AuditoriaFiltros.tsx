import { Card } from '@/shared/components/Card'

interface AuditoriaFiltrosProps {
  usuario?: string
  materia?: string
  accion?: string
  fechaDesde?: string
  fechaHasta?: string
  onUsuarioChange: (v: string) => void
  onMateriaChange: (v: string) => void
  onAccionChange: (v: string) => void
  onFechaDesdeChange: (v: string) => void
  onFechaHastaChange: (v: string) => void
}

export function AuditoriaFiltros({
  usuario, materia, accion, fechaDesde, fechaHasta,
  onUsuarioChange, onMateriaChange, onAccionChange, onFechaDesdeChange, onFechaHastaChange,
}: AuditoriaFiltrosProps) {
  return (
    <Card className="p-4">
      <div className="flex flex-wrap gap-4">
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Usuario</label>
          <input
            type="text"
            value={usuario ?? ''}
            onChange={(e) => onUsuarioChange(e.target.value || '')}
            placeholder="Nombre de usuario"
            className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Materia</label>
          <input
            type="text"
            value={materia ?? ''}
            onChange={(e) => onMateriaChange(e.target.value || '')}
            placeholder="Nombre de materia"
            className="block w-44 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Acción</label>
          <select
            value={accion ?? ''}
            onChange={(e) => onAccionChange(e.target.value || '')}
            className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todas</option>
            <option value="login">Login</option>
            <option value="logout">Logout</option>
            <option value="create">Creación</option>
            <option value="update">Actualización</option>
            <option value="delete">Eliminación</option>
            <option value="import">Importación</option>
            <option value="export">Exportación</option>
          </select>
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
