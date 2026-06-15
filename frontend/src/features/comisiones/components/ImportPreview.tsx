import { useState, useRef } from 'react'
import { useImportar } from '@/features/comisiones/hooks/useImportar'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import type { ActividadDetectada } from '@/features/comisiones/types/calificaciones'

interface ImportPreviewProps {
  comisionId: string
}

export function ImportPreview({ comisionId }: ImportPreviewProps) {
  const fileRef = useRef<HTMLInputElement>(null)
  const { upload, confirm } = useImportar(comisionId)
  const [actividades, setActividades] = useState<ActividadDetectada[]>([])
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setError(null)
    try {
      const result = await upload.mutateAsync(file)
      setActividades(result.actividades.map((a) => ({ ...a, seleccionada: true })))
      setSelectedIds(new Set(result.actividades.map((a) => a.actividad_id)))
    } catch {
      setError('Error al importar el archivo')
    }
  }

  const toggleActividad = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleConfirm = async () => {
    try {
      await confirm.mutateAsync(Array.from(selectedIds))
      setActividades([])
      setSelectedIds(new Set())
    } catch {
      setError('Error al confirmar la importación')
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Importar Calificaciones</h2>

      <input
        ref={fileRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleFileSelect}
        className="block text-sm text-gray-600 file:mr-4 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
      />

      {error && <Alert variant="error">{error}</Alert>}

      {upload.isPending && <p className="text-sm text-gray-500">Procesando archivo...</p>}

      {actividades.length > 0 && (
        <>
          <p className="text-sm text-gray-600">
            Se detectaron {actividades.length} actividades. Seleccione cuáles importar:
          </p>
          <ul className="space-y-2">
            {actividades.map((act) => (
              <li key={act.actividad_id} className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(act.actividad_id)}
                  onChange={() => toggleActividad(act.actividad_id)}
                  className="h-4 w-4 rounded border-gray-300 text-primary-600"
                />
                <span className="text-sm text-gray-900">{act.nombre}</span>
                <span className="text-xs text-gray-500">{act.tipo}</span>
                <span className="text-xs text-gray-400">{act.calificaciones_count} calificaciones</span>
              </li>
            ))}
          </ul>

          <Button onClick={handleConfirm} loading={confirm.isPending} disabled={selectedIds.size === 0}>
            Confirmar importación ({selectedIds.size})
          </Button>
        </>
      )}
    </div>
  )
}
