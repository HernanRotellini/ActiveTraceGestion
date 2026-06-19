import { useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { Combobox } from '@/shared/components/Combobox'
import { useAdminInstancias, useActualizarInstancia } from '@/features/encuentros/hooks/useEncuentros'
import { useMaterias } from '@/features/admin/hooks/useAdmin'
import type { AdminInstanciasFilters, EstadoInstancia, InstanciaEncuentroUpdate } from '@/features/encuentros/types'

const ESTADOS: EstadoInstancia[] = ['Programado', 'Realizado', 'Cancelado']

const ESTADO_CLASSES: Record<EstadoInstancia, string> = {
  Programado: 'bg-blue-100 text-blue-700',
  Realizado: 'bg-green-100 text-green-700',
  Cancelado: 'bg-gray-100 text-gray-600',
}

interface EditForm {
  id: string
  estado: EstadoInstancia
  meet_url: string
  video_url: string
  comentario: string
}

export default function EncuentrosListPage() {
  const [filters, setFilters] = useState<AdminInstanciasFilters>({})
  const { data, isLoading, error } = useAdminInstancias(filters)
  const actualizar = useActualizarInstancia()
  const [editing, setEditing] = useState<EditForm | null>(null)
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias()
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({
    value: m.id,
    label: `${m.nombre} (${m.codigo})`,
  }))

  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar los encuentros.'

  const handleSave = async () => {
    if (!editing) return
    const update: InstanciaEncuentroUpdate = {
      estado: editing.estado,
      meet_url: editing.meet_url || undefined,
      video_url: editing.video_url || undefined,
      comentario: editing.comentario || undefined,
    }
    try {
      await actualizar.mutateAsync({ id: editing.id, update })
      setToast({ message: 'Encuentro actualizado.', variant: 'success' })
      setEditing(null)
    } catch {
      setToast({ message: 'Error al actualizar el encuentro.', variant: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      {error && <Toast message={errorMessage} variant="error" onClose={() => {}} />}
      {toast && <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />}

      <h1 className="text-2xl font-bold text-gray-900">Encuentros</h1>

      <Card className="p-4">
        <div className="flex flex-wrap gap-4">
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Fecha desde</label>
            <input
              type="date"
              value={filters.fecha_desde ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_desde: e.target.value || undefined })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Fecha hasta</label>
            <input
              type="date"
              value={filters.fecha_hasta ?? ''}
              onChange={(e) => setFilters({ ...filters, fecha_hasta: e.target.value || undefined })}
              className="block w-40 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-xs font-medium text-gray-600">Estado</label>
            <select
              value={filters.estado ?? ''}
              onChange={(e) => setFilters({ ...filters, estado: (e.target.value as EstadoInstancia) || undefined })}
              className="block w-36 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              {ESTADOS.map((est) => <option key={est} value={est}>{est}</option>)}
            </select>
          </div>
          <div className="w-48">
            <Combobox
              label="Materia"
              items={materiaItems}
              value={filters.materia_id ?? ''}
              onChange={(val) => setFilters({ ...filters, materia_id: val || undefined })}
              placeholder="Buscar materia..."
              isLoading={loadingMaterias}
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
                  <th className="px-4 py-3">Fecha</th>
                  <th className="px-4 py-3">Hora</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Meet URL</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(data ?? []).map((inst) => (
                  <tr key={inst.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{inst.titulo}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(inst.fecha).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-gray-600">{inst.hora}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_CLASSES[inst.estado] ?? 'bg-gray-100 text-gray-600'}`}>
                        {inst.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {inst.meet_url ? <a href={inst.meet_url} target="_blank" rel="noreferrer" className="text-primary-600 hover:text-primary-800">Enlace</a> : '-'}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setEditing({
                          id: inst.id,
                          estado: inst.estado,
                          meet_url: inst.meet_url ?? '',
                          video_url: inst.video_url ?? '',
                          comentario: inst.comentario ?? '',
                        })}
                        className="font-medium text-primary-600 hover:text-primary-800"
                      >
                        Editar
                      </button>
                    </td>
                  </tr>
                ))}
                {(!data || data.length === 0) && (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-500">No hay encuentros registrados.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <Card className="w-full max-w-md p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Editar Encuentro</h2>
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Estado</label>
                <select
                  value={editing.estado}
                  onChange={(e) => setEditing({ ...editing, estado: e.target.value as EstadoInstancia })}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {ESTADOS.map((est) => <option key={est} value={est}>{est}</option>)}
                </select>
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Link Meet</label>
                <input
                  type="url"
                  value={editing.meet_url}
                  onChange={(e) => setEditing({ ...editing, meet_url: e.target.value })}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="https://..."
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Link Grabación</label>
                <input
                  type="url"
                  value={editing.video_url}
                  onChange={(e) => setEditing({ ...editing, video_url: e.target.value })}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="https://..."
                />
              </div>
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-700">Comentario interno</label>
                <textarea
                  value={editing.comentario}
                  onChange={(e) => setEditing({ ...editing, comentario: e.target.value })}
                  rows={3}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setEditing(null)}
                  className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={actualizar.isPending}
                  className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {actualizar.isPending ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
