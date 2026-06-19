import { useMemo, useState } from 'react'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import { Toast } from '@/shared/components/Toast'
import { useMonitor } from '@/features/monitores/hooks/useMonitor'
import { MonitorFilters } from '@/features/monitores/components/MonitorFilters'
import { MonitorTable } from '@/features/monitores/components/MonitorTable'
import type { MonitorFilters as MonitorFiltersType } from '@/features/monitores/types/monitores'

export default function MonitorGeneralPage() {
  const [filters, setFilters] = useState<MonitorFiltersType>({ per_page: 200 })
  const { data, isLoading, error } = useMonitor(filters)

  const errorMessage = error instanceof Error ? error.message : 'No se pudo cargar el monitor.'

  const stats = useMemo(() => {
    const items = data?.items ?? []
    const atrasados = items.filter((i) => i.atrasado).length
    return {
      total: data?.total ?? 0,
      atrasados,
      al_dia: (data?.total ?? 0) - atrasados,
      pct_atraso: data?.total ? Math.round((atrasados / data.total) * 100) : 0,
    }
  }, [data])

  return (
    <div className="space-y-6">
      {error && <Toast message={errorMessage} variant="error" onClose={() => {}} />}

      <h1 className="text-2xl font-bold text-gray-900">Monitor General</h1>

      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-gray-500">Total Alumnos</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{stats.total}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Al día</p>
          <p className="mt-1 text-2xl font-bold text-green-600">{stats.al_dia}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">Atrasados</p>
          <p className="mt-1 text-2xl font-bold text-red-600">{stats.atrasados}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-gray-500">% Atraso</p>
          <p className="mt-1 text-2xl font-bold text-orange-600">{stats.pct_atraso}%</p>
        </Card>
      </div>

      <Card className="p-4">
        <MonitorFilters filters={filters} onChange={setFilters} />
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12"><Spinner /></div>
      ) : (
        <Card>
          {data && data.total > 0 && (
            <div className="border-b px-4 py-2 text-sm text-gray-500">
              {data.total} {data.total === 1 ? 'alumno' : 'alumnos'} encontrados
            </div>
          )}
          <MonitorTable items={data?.items} />
        </Card>
      )}
    </div>
  )
}
