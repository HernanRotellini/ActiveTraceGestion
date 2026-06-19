import { useState, useRef } from 'react'
import { useImportar } from '@/features/comisiones/hooks/useImportar'
import { Button } from '@/shared/components/Button'
import { Toast } from '@/shared/components/Toast'
import type { ActividadDetectada } from '@/features/comisiones/types/calificaciones'

interface ImportPreviewProps {
  materiaId: string
  cohorteId: string
}

export function ImportPreview({ materiaId, cohorteId }: ImportPreviewProps) {
  const fileRef = useRef<HTMLInputElement>(null)
  const { upload, confirm } = useImportar(materiaId, cohorteId)
  const [previewToken, setPreviewToken] = useState('')
  const [actividades, setActividades] = useState<ActividadDetectada[]>([])
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [toast, setToast] = useState<{ message: string; variant: 'success' | 'error' } | null>(null)

  const handleFileSelect = async () => {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    try {
      const result = await upload.mutateAsync(file)
      setPreviewToken(result.preview_token)
      setActividades(result.actividades)
      setSelectedIds(new Set(result.actividades.map((actividad) => actividad.nombre)))
      setToast({
        message: `Archivo procesado: ${result.total_rows} filas, ${result.alumnos_match.length} alumnos vinculados.`,
        variant: 'success',
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al importar el archivo.'
      setToast({ message, variant: 'error' })
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
    if (!previewToken) {
      setToast({ message: 'Primero procesá un archivo.', variant: 'error' })
      return
    }
    try {
      const result = await confirm.mutateAsync({
        previewToken,
        actividadIds: Array.from(selectedIds),
      })
      setActividades([])
      setSelectedIds(new Set())
      setPreviewToken('')
      setToast({
        message: `Importación confirmada: ${result.registros_creados} calificaciones creadas.`,
        variant: 'success',
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error al confirmar la importación.'
      setToast({ message, variant: 'error' })
    }
  }

  return (
    <div className="space-y-4">
      {toast && (
        <Toast
          message={toast.message}
          variant={toast.variant}
          onClose={() => setToast(null)}
        />
      )}

      <h2 className="text-lg font-semibold">Importar Calificaciones</h2>

      <input
        ref={fileRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleFileSelect}
        className="block text-sm text-gray-600 file:mr-4 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
      />

      {upload.isPending && <p className="text-sm text-gray-500">Procesando archivo...</p>}

      {actividades.length > 0 && (
        <>
          <p className="text-sm text-gray-600">
            Se detectaron {actividades.length} actividades. Seleccioná cuáles importar:
          </p>
          <ul className="space-y-2">
            {actividades.map((act) => (
              <li key={act.nombre} className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(act.nombre)}
                  onChange={() => toggleActividad(act.nombre)}
                  className="h-4 w-4 rounded border-gray-300 text-primary-600"
                />
                <span className="text-sm text-gray-900">{act.nombre}</span>
                <span className="text-xs text-gray-500">{act.tipo}</span>
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
