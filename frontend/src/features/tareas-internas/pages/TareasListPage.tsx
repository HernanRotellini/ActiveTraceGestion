import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Combobox } from '@/shared/components/Combobox'
import { useTareasList } from '@/features/tareas-internas/hooks/useTareas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { TareasFilters, Prioridad } from '@/features/tareas-internas/types'

const PRIORIDAD_CLASSES: Record<Prioridad, string> = {
  baja: 'bg-gray-100 text-gray-600',
  media: 'bg-blue-100 text-blue-700',
  alta: 'bg-orange-100 text-orange-700',
  critica: 'bg-red-100 text-red-700',
}

const ESTADO_CLASSES: Record<string, string> = {
  pendiente: 'bg-yellow-100 text-yellow-700',
  en_progreso: 'bg-blue-100 text-blue-700',
  completada: 'bg-green-100 text-green-700',
  cancelada: 'bg-gray-100 text-gray-600',
}

export default function TareasListPage() {
  const [filters, setFilters] = useState<TareasFilters>({ page: 1, limit: 20 })
  const { data, isLoading } = useTareasList(filters)

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} (${u.email})`,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tareas Internas</h1>
        <Link
          to="/coordinacion/tareas/nuevo"
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
        >
          Nueva Tarea
        </Link>
      </div>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Estado</label>
            <select
              value={filters.estado ?? ''}
              onChange={(e) => setFilters({ ...filters, estado: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="pendiente">Pendiente</option>
              <option value="en_progreso">En progreso</option>
              <option value="completada">Completada</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Prioridad</label>
            <select
              value={filters.prioridad ?? ''}
              onChange={(e) => setFilters({ ...filters, prioridad: e.target.value || undefined, page: 1 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todas</option>
              <option value="baja">Baja</option>
              <option value="media">Media</option>
              <option value="alta">Alta</option>
              <option value="critica">Crítica</option>
            </select>
          </div>
          <div className="w-48">
            <Combobox
              label="Asignado"
              items={usuarioItems}
              value={filters.asignado_id ?? ''}
              onChange={(val) => setFilters({ ...filters, asignado_id: val || undefined, page: 1 })}
              placeholder="Buscar usuario..."
              isLoading={loadingUsuarios}
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Desde</label>
            <input
              type="date"
              value={filters.fecha_desde ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value || undefined, page: 1 })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Título</th>
                  <th className="px-4 py-3">Prioridad</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Asignado</th>
                  <th className="px-4 py-3">Fecha límite</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data?.items.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{t.titulo}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${PRIORIDAD_CLASSES[t.prioridad]}`}>{t.prioridad}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_CLASSES[t.estado]}`}>{t.estado}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{t.asignado_nombre ?? '-'}</td>
                    <td className="px-4 py-3 text-gray-600">{t.fecha_limite ? new Date(t.fecha_limite).toLocaleDateString() : '-'}</td>
                    <td className="px-4 py-3">
                      <Link to={`/coordinacion/tareas/${t.id}`} className="text-primary-600 hover:text-primary-800 font-medium">Ver</Link>
                    </td>
                  </tr>
                ))}
                {(!data?.items || data.items.length === 0) && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay tareas registradas.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {data && data.total > (filters.limit ?? 20) && (
            <div className="flex items-center justify-between border-t px-4 py-3">
              <span className="text-sm text-gray-600">
                {((filters.page ?? 1) - 1) * (filters.limit ?? 20) + 1}-{Math.min((filters.page ?? 1) * (filters.limit ?? 20), data.total)} de {data.total}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) - 1 })}
                  disabled={(filters.page ?? 1) <= 1}
                  className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
                >Anterior</button>
                <button
                  onClick={() => setFilters({ ...filters, page: (filters.page ?? 1) + 1 })}
                  disabled={(filters.page ?? 1) * (filters.limit ?? 20) >= data.total}
                  className="rounded-lg border px-3 py-1 text-sm disabled:opacity-50 hover:bg-gray-50"
                >Siguiente</button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
