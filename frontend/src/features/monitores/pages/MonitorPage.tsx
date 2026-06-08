import { useState } from 'react'
import { useMonitor } from '@/features/monitores/hooks/useMonitor'
import { MonitorFilters } from '@/features/monitores/components/MonitorFilters'
import { MonitorTable } from '@/features/monitores/components/MonitorTable'
import { Card } from '@/shared/components/Card'
import { Spinner } from '@/shared/components/Spinner'
import type { MonitorFilters as MonitorFiltersType } from '@/features/monitores/types/monitores'

export default function MonitorPage() {
  const [filters, setFilters] = useState<MonitorFiltersType>({})
  const { data, isLoading } = useMonitor(filters)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Monitor de Alumnos</h1>

      <Card className="p-4">
        <MonitorFilters filters={filters} onChange={setFilters} />
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <Card>
          <MonitorTable data={data} />
        </Card>
      )}
    </div>
  )
}
