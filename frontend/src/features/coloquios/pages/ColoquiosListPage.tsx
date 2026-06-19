import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { Combobox } from '@/shared/components/Combobox'
import { useColoquiosList, useMetricasColoquios } from '@/features/coloquios/hooks/useColoquios'
import { useMaterias } from '@/features/admin/hooks/useAdmin'
import type { ColoquiosFilters } from '@/features/coloquios/types'

export default function ColoquiosListPage() {
  const [filters, setFilters] = useState<ColoquiosFilters>({})
  const { data, isLoading, error } = useColoquiosList(filters)
  const { data: metricas } = useMetricasColoquios()

  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias()
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({
    value: m.id,
    label: `${m.nombre} (${m.codigo})`,
  }))

  const errorMessage = error instanceof Error ? error.message : 'No se pudieron cargar los coloquios.'

  return (
    <div className="space-y-6">
      {error && <Toast message={errorMessage} variant="error" onClose={() => {}} />}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Coloquios</h1>
        <Link
          to="/coordinacion/coloquios/nuevo"
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700"
        >
          Nueva Convocatoria
        </Link>
      </div>

      {metricas && (
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: 'Convocatorias activas', value: metricas.convocatorias_activas },
            { label: 'Alumnos convocados', value: metricas.alumnos_convocados },
            { label: 'Reservas activas', value: metricas.reservas_activas },
            { label: 'Notas registradas', value: metricas.notas_registradas },
          ].map((stat) => (
            <Card key={stat.label} className="p-4 text-center">
              <p className="text-2xl font-bold text-primary-600">{stat.value}</p>
              <p className="mt-1 text-sm text-gray-500">{stat.label}</p>
            </Card>
          ))}
        </div>
      )}

      <Card className="p-4">
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
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b bg-gray-50 text-xs uppercase text-gray-600">
                <tr>
                  <th className="px-4 py-3">Tipo</th>
                  <th className="px-4 py-3">Instancia</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3">Turnos</th>
                  <th className="px-4 py-3">Alumnos</th>
                  <th className="px-4 py-3">Reservas</th>
                  <th className="px-4 py-3">Cupos libres</th>
                  <th className="px-4 py-3">Creada</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {(data ?? []).map((col) => (
                  <tr key={col.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900">{col.tipo}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{col.instancia}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        col.estado === 'cerrado' ? 'bg-gray-100 text-gray-600'
                        : 'bg-green-100 text-green-700'
                      }`}>{col.estado}</span>
                    </td>
                    <td className="px-4 py-3 text-center text-gray-600">{col.total_turnos}</td>
                    <td className="px-4 py-3 text-center text-gray-600">{col.alumnos_convocados}</td>
                    <td className="px-4 py-3 text-center text-gray-600">{col.reservas_activas}</td>
                    <td className="px-4 py-3 text-center text-gray-600">{col.cupos_libres}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(col.created_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <Link to={`/coordinacion/coloquios/${col.id}`} className="font-medium text-primary-600 hover:text-primary-800">Ver</Link>
                    </td>
                  </tr>
                ))}
                {(!data || data.length === 0) && (
                  <tr>
                    <td colSpan={9} className="px-4 py-8 text-center text-gray-500">No hay convocatorias registradas.</td>
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
