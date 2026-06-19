import { useEffect, useState } from 'react'
import { useEntregasPendientes } from '@/features/entregas-sin-corregir/hooks/useEntregasPendientes'
import { EntregasTable } from '@/features/entregas-sin-corregir/components/EntregasTable'
import { ExportButton } from '@/features/entregas-sin-corregir/components/ExportButton'
import { ImportarReporteLms } from '@/features/entregas-sin-corregir/components/ImportarReporteLms'
import { Spinner } from '@/shared/components/Spinner'
import { Card } from '@/shared/components/Card'
import { Toast } from '@/shared/components/Toast'

export default function EntregasPendientesPage() {
  const [comision, setComision] = useState<string>('')
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)
  const { query, exportMutation, importMutation } = useEntregasPendientes(comision.trim() || undefined)

  const notify = (message: string, variant: 'success' | 'error') => setToast({ message, variant })

  // Surface load failures con el Toast compartido (además del estado inline).
  useEffect(() => {
    if (query.isError) {
      notify('No se pudieron cargar las entregas pendientes.', 'error')
    }
  }, [query.isError])

  const handleExport = () => {
    exportMutation.mutate(undefined, {
      onSuccess: () => notify('Exportación generada correctamente.', 'success'),
      onError: () => notify('No se pudo generar la exportación.', 'error'),
    })
  }

  const items = query.data?.items
  const total = query.data?.total ?? 0

  return (
    <div className="space-y-6">
      {toast && (
        <Toast message={toast.message} variant={toast.variant} onClose={() => setToast(null)} />
      )}

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Entregas sin Corregir</h1>
        <ExportButton
          onExport={handleExport}
          isLoading={exportMutation.isPending}
          disabled={query.isLoading || query.isError || total === 0}
        />
      </div>

      <ImportarReporteLms
        onImport={(args) => importMutation.mutateAsync(args)}
        isImporting={importMutation.isPending}
        onNotify={notify}
      />

      <Card className="p-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Comisión</label>
        <input
          type="text"
          value={comision}
          onChange={(e) => setComision(e.target.value)}
          placeholder="Ej: A o B"
          className="block w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </Card>

      {query.isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : query.isError ? (
        <Card className="p-12 text-center">
          <p className="text-red-700">No se pudieron cargar las entregas pendientes. Reintentá en unos segundos.</p>
        </Card>
      ) : (
        <Card>
          <EntregasTable data={items} />
        </Card>
      )}
    </div>
  )
}
