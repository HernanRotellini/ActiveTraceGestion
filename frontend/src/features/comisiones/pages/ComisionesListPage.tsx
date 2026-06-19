import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { useMisComisiones } from '@/features/comisiones/hooks/useMisComisiones'
import type { MisComisionesFilters } from '@/features/comisiones/types/misComisiones'

const ROLE_LABELS: Record<string, string> = {
  PROFESOR: 'Profesor',
  TUTOR: 'Tutor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
}

function formatDate(value: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString()
}

function shortId(value: string | null) {
  return value ? `${value.slice(0, 8)}...` : '-'
}

export default function ComisionesListPage() {
  const [filters, setFilters] = useState<MisComisionesFilters>({})
  const [materiaSearch, setMateriaSearch] = useState('')
  const [carreraSearch, setCarreraSearch] = useState('')
  const [cohorteSearch, setCohorteSearch] = useState('')
  const [toastClosed, setToastClosed] = useState(false)
  const { data: comisiones, isLoading, error } = useMisComisiones(filters)

  const updateFilter = <K extends keyof MisComisionesFilters>(key: K, value: MisComisionesFilters[K] | '') => {
    setFilters((current) => ({
      ...current,
      [key]: value || undefined,
    }))
  }

  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar tus comisiones.'
  const filteredComisiones = (comisiones ?? []).filter((item) => {
    const materia = (item.materia_nombre ?? item.materia_id ?? '').toLowerCase()
    const carrera = (item.carrera_nombre ?? item.carrera_id ?? '').toLowerCase()
    const cohorte = (item.cohorte_nombre ?? item.cohorte_id ?? '').toLowerCase()
    return (
      materia.includes(materiaSearch.toLowerCase()) &&
      carrera.includes(carreraSearch.toLowerCase()) &&
      cohorte.includes(cohorteSearch.toLowerCase())
    )
  })

  return (
    <div className="space-y-6">
      {error && !toastClosed && (
        <Toast message={errorMessage} variant="error" onClose={() => setToastClosed(true)} />
      )}

      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mis Comisiones</h1>
        <p className="mt-1 text-sm text-gray-500">
          Materias y comisiones asociadas a tus asignaciones vigentes o históricas.
        </p>
      </div>

      <Card className="p-4">
        <div className="grid gap-4 md:grid-cols-5">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Estado</label>
            <select
              value={filters.estado ?? ''}
              onChange={(event) => updateFilter('estado', event.target.value as MisComisionesFilters['estado'] | '')}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              <option value="vigente">Vigente</option>
              <option value="vencida">Vencida</option>
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Rol</label>
            <select
              value={filters.rol ?? ''}
              onChange={(event) => updateFilter('rol', event.target.value)}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Todos</option>
              {Object.entries(ROLE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Materia</label>
            <input
              type="text"
              value={materiaSearch}
              onChange={(event) => setMateriaSearch(event.target.value)}
              placeholder="Buscar materia..."
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Carrera</label>
            <input
              type="text"
              value={carreraSearch}
              onChange={(event) => setCarreraSearch(event.target.value)}
              placeholder="Buscar carrera..."
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Cohorte</label>
            <input
              type="text"
              value={cohorteSearch}
              onChange={(event) => setCohorteSearch(event.target.value)}
              placeholder="Buscar cohorte..."
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Materia</th>
                  <th className="px-4 py-3">Carrera</th>
                  <th className="px-4 py-3">Cohorte</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Comisiones</th>
                  <th className="px-4 py-3">Vigencia</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredComisiones.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {item.materia_nombre ?? shortId(item.materia_id)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {item.carrera_nombre ?? shortId(item.carrera_id)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {item.cohorte_nombre ?? shortId(item.cohorte_id)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{ROLE_LABELS[item.rol] ?? item.rol}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {item.comisiones?.length ? item.comisiones.join(', ') : 'Sin comisiones cargadas'}
                    </td>
                    <td className="px-4 py-3 text-gray-600">
                      {formatDate(item.desde)} - {formatDate(item.hasta)}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        item.estado_vigencia === 'vigente'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {item.estado_vigencia === 'vigente' ? 'Vigente' : 'Vencida'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/docente/comisiones/${item.id}`}
                        className="font-medium text-primary-600 hover:text-primary-800"
                      >
                        Ver
                      </Link>
                    </td>
                  </tr>
                ))}
                {filteredComisiones.length === 0 && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                      No hay comisiones asignadas.
                    </td>
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
