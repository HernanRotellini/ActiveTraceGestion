import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { useAvisosList } from '@/features/avisos/hooks/useAvisos'
import type { AvisosFilters } from '@/features/avisos/types'

const SEVERIDAD_BADGES: Record<string, string> = {
  Info: 'bg-blue-100 text-blue-700',
  Advertencia: 'bg-yellow-100 text-yellow-700',
  Critico: 'bg-red-100 text-red-700',
}

const ALCANCE_LABELS: Record<string, string> = {
  Global: 'Global',
  PorMateria: 'Por materia',
  PorCohorte: 'Por cohorte',
  PorRol: 'Por rol',
}

export default function AvisosListPage() {
  const [filters, setFilters] = useState<AvisosFilters>({})
  const { data, isLoading, error } = useAvisosList(filters)

  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar los avisos.'

  return (
    <div className="space-y-6">
      {error && <Toast message={errorMessage} variant="error" onClose={() => {}} />}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Avisos</h1>
        <Link
          to="/coordinacion/avisos/nuevo"
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
        >
          Nuevo Aviso
        </Link>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Alcance</label>
            <select
              value={filters.alcance ?? ''}
              onChange={(e) => setFilters({ ...filters, alcance: e.target.value || undefined })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="Global">Global</option>
              <option value="PorMateria">Por materia</option>
              <option value="PorCohorte">Por cohorte</option>
              <option value="PorRol">Por rol</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Severidad</label>
            <select
              value={filters.severidad ?? ''}
              onChange={(e) => setFilters({ ...filters, severidad: e.target.value || undefined })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todas</option>
              <option value="Info">Info</option>
              <option value="Advertencia">Advertencia</option>
              <option value="Critico">Crítico</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Estado</label>
            <select
              value={filters.activo === undefined ? '' : String(filters.activo)}
              onChange={(e) => setFilters({ ...filters, activo: e.target.value === '' ? undefined : e.target.value === 'true' })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <div className="space-y-4">
          {(data ?? []).map((aviso) => (
            <Link key={aviso.id} to={`/coordinacion/avisos/${aviso.id}`}>
              <Card className="p-4 transition-shadow hover:shadow-md">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{aviso.titulo}</h3>
                  </div>
                  <span className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${SEVERIDAD_BADGES[aviso.severidad] ?? 'bg-gray-100 text-gray-600'}`}>
                    {aviso.severidad}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                  <span>{new Date(aviso.created_at).toLocaleDateString()}</span>
                  <span>Alcance: {ALCANCE_LABELS[aviso.alcance] ?? aviso.alcance}</span>
                  {aviso.requiere_ack && (
                    <span className="font-medium text-amber-600">Requiere confirmación</span>
                  )}
                  {aviso.fin_en && (
                    <span>Vence: {new Date(aviso.fin_en).toLocaleDateString()}</span>
                  )}
                </div>
              </Card>
            </Link>
          ))}
          {(!data || data.length === 0) && !isLoading && (
            <Card className="p-12 text-center">
              <p className="text-gray-500">No hay avisos registrados.</p>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
