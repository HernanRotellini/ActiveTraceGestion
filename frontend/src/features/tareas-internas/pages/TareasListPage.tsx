import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { Combobox } from '@/shared/components/Combobox'
import { useTareasList } from '@/features/tareas-internas/hooks/useTareas'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { TareasFilters, TareaEstado } from '@/features/tareas-internas/types'

const ESTADO_CLASSES: Record<TareaEstado, string> = {
  'Pendiente': 'bg-yellow-100 text-yellow-700',
  'En progreso': 'bg-blue-100 text-blue-700',
  'Resuelta': 'bg-green-100 text-green-700',
  'Cancelada': 'bg-gray-100 text-gray-600',
}

const ESTADOS: TareaEstado[] = ['Pendiente', 'En progreso', 'Resuelta', 'Cancelada']

export default function TareasListPage() {
  const [filters, setFilters] = useState<TareasFilters>({ limit: 100, offset: 0 })
  const { data, isLoading, error } = useTareasList(filters)

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} ${u.apellidos} (${u.email})`,
  }))
  const usuariosById = useMemo(
    () => new Map((usuariosResp?.items ?? []).map((u) => [u.id, `${u.nombre} ${u.apellidos}`])),
    [usuariosResp?.items],
  )

  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar las tareas.'

  return (
    <div className="space-y-6">
      {error && <Toast message={errorMessage} variant="error" onClose={() => {}} />}

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
              onChange={(e) => setFilters({ ...filters, estado: (e.target.value as TareaEstado) || undefined, offset: 0 })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              {ESTADOS.map((est) => <option key={est} value={est}>{est}</option>)}
            </select>
          </div>
          <div className="w-52">
            <Combobox
              label="Asignado a"
              items={usuarioItems}
              value={filters.asignado_a ?? ''}
              onChange={(val) => setFilters({ ...filters, asignado_a: val || undefined, offset: 0 })}
              placeholder="Buscar usuario..."
              isLoading={loadingUsuarios}
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Búsqueda</label>
            <input
              type="text"
              value={filters.search ?? ''}
              onChange={(e) => setFilters({ ...filters, search: e.target.value || undefined, offset: 0 })}
              placeholder="Título..."
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
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Asignado a</th>
                  <th className="px-4 py-3">Asignado por</th>
                  <th className="px-4 py-3">Creada</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(data ?? []).map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{t.titulo}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_CLASSES[t.estado] ?? 'bg-gray-100 text-gray-600'}`}>{t.estado}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{usuariosById.get(t.asignado_a) ?? t.asignado_a.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-gray-600">{usuariosById.get(t.asignado_por) ?? t.asignado_por.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(t.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <Link to={`/coordinacion/tareas/${t.id}`} className="font-medium text-primary-600 hover:text-primary-800">Ver</Link>
                    </td>
                  </tr>
                ))}
                {(!data || data.length === 0) && !isLoading && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay tareas registradas.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
