import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Combobox } from '@/shared/components/Combobox'
import { Toast } from '@/shared/components/Toast'
import { useAsignacionesList } from '@/features/equipos-docentes/hooks/useEquipos'
import { useCarreras, useCohortesList, useMaterias, useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { AsignacionListFilters } from '@/features/equipos-docentes/types'

const ROLE_LABELS: Record<string, string> = {
  PROFESOR: 'Profesor',
  TUTOR: 'Tutor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
  ADMIN: 'Admin',
  FINANZAS: 'Finanzas',
}

function formatDate(value: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleDateString()
}

function shortId(value: string | null) {
  return value ? `${value.slice(0, 8)}...` : '-'
}

export default function EquiposListPage() {
  const [filters, setFilters] = useState<AsignacionListFilters>({})
  const [toastClosed, setToastClosed] = useState(false)
  const { data: asignaciones, isLoading, error } = useAsignacionesList(filters)
  const { data: carrerasResp, isLoading: loadingCarreras } = useCarreras()
  const { data: cohortesResp, isLoading: loadingCohortes } = useCohortesList()
  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias()
  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()

  const carrerasById = useMemo(
    () => new Map((carrerasResp?.items ?? []).map((item) => [item.id, item.nombre])),
    [carrerasResp?.items],
  )
  const cohortesById = useMemo(
    () => new Map((cohortesResp?.items ?? []).map((item) => [item.id, item.nombre])),
    [cohortesResp?.items],
  )
  const materiasById = useMemo(
    () => new Map((materiasResp?.items ?? []).map((item) => [item.id, item.nombre])),
    [materiasResp?.items],
  )
  const usuariosById = useMemo(
    () => new Map((usuariosResp?.items ?? []).map((item) => [item.id, `${item.nombre} ${item.apellidos}`])),
    [usuariosResp?.items],
  )

  const materiaItems = (materiasResp?.items ?? []).map((item) => ({
    value: item.id,
    label: `${item.nombre} (${item.codigo})`,
  }))
  const usuarioItems = (usuariosResp?.items ?? []).map((item) => ({
    value: item.id,
    label: `${item.nombre} ${item.apellidos} (${item.email})`,
  }))

  const updateFilter = <K extends keyof AsignacionListFilters>(key: K, value: AsignacionListFilters[K] | '') => {
    setFilters((current) => ({ ...current, [key]: value || undefined }))
  }

  const loadingCatalogs = loadingCarreras || loadingCohortes || loadingMaterias || loadingUsuarios
  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar las asignaciones.'

  return (
    <div className="space-y-6">
      {error && !toastClosed && (
        <Toast message={errorMessage} variant="error" onClose={() => setToastClosed(true)} />
      )}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Equipos Docentes</h1>
          <p className="mt-1 text-sm text-gray-500">Asignaciones de docentes a materias, cohortes y comisiones.</p>
        </div>
        <Link
          to="/coordinacion/equipos-docentes/nuevo"
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
        >
          Nueva asignación
        </Link>
      </div>

      <Card className="p-4">
        <div className="grid gap-4 md:grid-cols-3">
          <Combobox
            label="Materia"
            items={materiaItems}
            value={filters.materia_id ?? ''}
            onChange={(value) => updateFilter('materia_id', value)}
            placeholder="Todas"
            isLoading={loadingMaterias}
          />
          <Combobox
            label="Docente"
            items={usuarioItems}
            value={filters.usuario_id ?? ''}
            onChange={(value) => updateFilter('usuario_id', value)}
            placeholder="Todos"
            isLoading={loadingUsuarios}
          />
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
        </div>
      </Card>

      {isLoading || loadingCatalogs ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Docente</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Materia</th>
                  <th className="px-4 py-3">Carrera</th>
                  <th className="px-4 py-3">Cohorte</th>
                  <th className="px-4 py-3">Comisiones</th>
                  <th className="px-4 py-3">Vigencia</th>
                  <th className="px-4 py-3">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {asignaciones?.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">
                      {usuariosById.get(item.usuario_id) ?? shortId(item.usuario_id)}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{ROLE_LABELS[item.rol] ?? item.rol}</td>
                    <td className="px-4 py-3 text-gray-600">{materiasById.get(item.materia_id ?? '') ?? shortId(item.materia_id)}</td>
                    <td className="px-4 py-3 text-gray-600">{carrerasById.get(item.carrera_id ?? '') ?? shortId(item.carrera_id)}</td>
                    <td className="px-4 py-3 text-gray-600">{cohortesById.get(item.cohorte_id ?? '') ?? shortId(item.cohorte_id)}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {item.comisiones?.length ? item.comisiones.join(', ') : 'Sin comisiones cargadas'}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{formatDate(item.desde)} - {formatDate(item.hasta)}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        item.estado_vigencia === 'vigente' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {item.estado_vigencia === 'vigente' ? 'Vigente' : 'Vencida'}
                      </span>
                    </td>
                  </tr>
                ))}
                {(!asignaciones || asignaciones.length === 0) && (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                      No hay asignaciones registradas.
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
