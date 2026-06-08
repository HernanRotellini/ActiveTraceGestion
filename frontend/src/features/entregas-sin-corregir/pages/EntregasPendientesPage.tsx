import { useState } from 'react'
import { useEntregasPendientes } from '@/features/entregas-sin-corregir/hooks/useEntregasPendientes'
import { EntregasTable } from '@/features/entregas-sin-corregir/components/EntregasTable'
import { ExportButton } from '@/features/entregas-sin-corregir/components/ExportButton'
import { Spinner } from '@/shared/components/Spinner'
import { Card } from '@/shared/components/Card'

export default function EntregasPendientesPage() {
  const [comisionFilter, setComisionFilter] = useState<string>('')
  const { query, exportMutation } = useEntregasPendientes(comisionFilter || undefined)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Entregas sin Corregir</h1>
        <ExportButton onExport={() => exportMutation.mutate()} isLoading={exportMutation.isPending} />
      </div>

      <Card className="p-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Filtrar por comisión</label>
        <input
          type="text"
          value={comisionFilter}
          onChange={(e) => setComisionFilter(e.target.value)}
          placeholder="ID de comisión (opcional)"
          className="block w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </Card>

      {query.isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <Card>
          <EntregasTable data={query.data} />
        </Card>
      )}
    </div>
  )
}
