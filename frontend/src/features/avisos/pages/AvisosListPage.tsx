import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { useAvisosList } from '@/features/avisos/hooks/useAvisos'
import type { AvisosFilters } from '@/features/avisos/types'

const SEVERIDAD_BADGES: Record<string, string> = {
  Info: 'bg-blue-100 text-blue-700',
  Advertencia: 'bg-yellow-100 text-yellow-700',
  Critico: 'bg-red-100 text-red-700',
}

export default function AvisosListPage() {
  const [filters, setFilters] = useState<AvisosFilters>({ page: 1, limit: 20 })
  const { data, isLoading, error } = useAvisosList(filters)

  if (error) {
    return (
      <Card className="p-12 text-center">
        <p className="text-red-500">Error al cargar avisos: {(error as Error).message}</p>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
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
            <label className="block text-xs font-medium text-gray-600">Activo</label>
            <select
              value={filters.activo ?? ''}
              onChange={(e) => setFilters({ ...filters, activo: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Severidad</label>
            <select
              value={filters.severidad ?? ''}
              onChange={(e) => setFilters({ ...filters, severidad: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todas</option>
              <option value="Info">Info</option>
              <option value="Advertencia">Advertencia</option>
              <option value="Critico">Crítico</option>
            </select>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <div className="space-y-4">
          {data?.items?.map((aviso) => (
            <Link key={aviso.id} to={`/coordinacion/avisos/${aviso.id}`}>
              <Card className="p-4 transition-shadow hover:shadow-md">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{aviso.titulo}</h3>
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">{aviso.cuerpo}</p>
                  </div>
                  <span className={`inline-flex shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${SEVERIDAD_BADGES[aviso.severidad] ?? 'bg-gray-100 text-gray-600'}`}>
                    {aviso.severidad}
                  </span>
                </div>
                <div className="mt-2 flex items-center gap-4 text-xs text-gray-400">
                  <span>{new Date(aviso.created_at).toLocaleDateString()}</span>
                  <span>Alcance: {aviso.alcance}</span>
                  {aviso.requiere_ack && (
                    <span className="font-medium text-amber-600">Requiere confirmación</span>
                  )}
                </div>
              </Card>
            </Link>
          ))}
          {(!data?.items || data.items.length === 0) && (
            <Card className="p-12 text-center">
              <p className="text-gray-500">No hay avisos registrados.</p>
            </Card>
          )}
        </div>
      )}

      {data && data.total > (filters.limit ?? 20) && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">
            {((filters.page ?? 1) - 1) * (filters.limit ?? 20) + 1}-{Math.min((filters.page ?? 1) * (filters.limit ?? 20), data.total)} de {data.total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) - 1 })}
              disabled={(filters.page ?? 1) <= 1}
              className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) + 1 })}
              disabled={(filters.page ?? 1) * (filters.limit ?? 20) >= data.total}
              className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
