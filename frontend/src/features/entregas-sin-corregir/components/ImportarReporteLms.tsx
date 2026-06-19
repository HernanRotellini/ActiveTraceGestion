import { useRef, useState } from 'react'
import { isAxiosError } from 'axios'
import { Card } from '@/shared/components/Card'
import { Button } from '@/shared/components/Button'
import { useCarreras, useCohortes, useMaterias } from '@/features/admin/hooks/useAdmin'
import { ApiError } from '@/shared/types/api'
import type { CompletionReportResponse } from '@/features/entregas-sin-corregir/types/entregas'

interface ImportarReporteLmsProps {
  onImport: (args: { materiaId: string; cohorteId: string; file: File }) => Promise<CompletionReportResponse>
  isImporting: boolean
  onNotify: (message: string, variant: 'success' | 'error') => void
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message || 'No se pudo procesar el reporte LMS.'
  if (isAxiosError<{ detail?: string }>(error)) {
    return error.response?.data?.detail ?? 'No se pudo procesar el reporte LMS.'
  }
  return 'No se pudo procesar el reporte LMS.'
}

export function ImportarReporteLms({ onImport, isImporting, onNotify }: ImportarReporteLmsProps) {
  const fileRef = useRef<HTMLInputElement>(null)
  const [carreraId, setCarreraId] = useState('')
  const [cohorteId, setCohorteId] = useState('')
  const [materiaId, setMateriaId] = useState('')
  const [resultado, setResultado] = useState<CompletionReportResponse | null>(null)

  const { data: carreras } = useCarreras()
  const { data: cohortes } = useCohortes(carreraId || undefined)
  const { data: materias } = useMaterias(carreraId || undefined, cohorteId || undefined)

  const handleSubmit = async () => {
    const file = fileRef.current?.files?.[0]
    if (!materiaId || !cohorteId) {
      onNotify('Seleccioná carrera, cohorte y materia antes de cargar el reporte.', 'error')
      return
    }
    if (!file) {
      onNotify('Elegí un archivo de reporte LMS para cargar.', 'error')
      return
    }
    try {
      const data = await onImport({ materiaId, cohorteId, file })
      setResultado(data)
      const cantidad = data.posibles_entregas_sin_corregir.length
      if (cantidad === 0) {
        onNotify('Reporte procesado: no se detectaron entregas sin corregir.', 'success')
      } else {
        onNotify(
          `Reporte procesado: ${cantidad} ${cantidad === 1 ? 'posible entrega' : 'posibles entregas'} sin corregir.`,
          'success',
        )
      }
    } catch (error) {
      setResultado(null)
      onNotify(getErrorMessage(error), 'error')
    }
  }

  return (
    <Card className="space-y-4 p-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">Importar reporte LMS de finalización</h2>
        <p className="text-sm text-gray-600">
          Cruzá el reporte de finalización del LMS con las calificaciones para detectar entregas sin corregir.
        </p>
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Carrera</label>
          <select
            value={carreraId}
            onChange={(e) => {
              setCarreraId(e.target.value)
              setCohorteId('')
              setMateriaId('')
            }}
            className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Seleccioná una carrera</option>
            {carreras?.items?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Cohorte</label>
          <select
            value={cohorteId}
            onChange={(e) => {
              setCohorteId(e.target.value)
              setMateriaId('')
            }}
            disabled={!carreraId}
            className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="">Seleccioná una cohorte</option>
            {cohortes?.items?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-gray-600">Materia</label>
          <select
            value={materiaId}
            onChange={(e) => setMateriaId(e.target.value)}
            disabled={!cohorteId}
            className="block w-52 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="">Seleccioná una materia</option>
            {materias?.items?.map((m) => (
              <option key={m.id} value={m.id}>{m.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <input
          ref={fileRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          aria-label="Archivo de reporte LMS de finalización"
          className="block text-sm text-gray-600 file:mr-4 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
        />
        <Button onClick={handleSubmit} loading={isImporting}>
          Procesar reporte
        </Button>
      </div>

      {resultado && resultado.posibles_entregas_sin_corregir.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left text-gray-600">
                <th className="p-3">Alumno</th>
                <th className="p-3">Actividad</th>
              </tr>
            </thead>
            <tbody>
              {resultado.posibles_entregas_sin_corregir.map((p, idx) => (
                <tr key={`${p.alumno_apellidos}-${p.alumno_nombre}-${p.actividad}-${idx}`} className="border-b last:border-0">
                  <td className="p-3">{p.alumno_apellidos}, {p.alumno_nombre}</td>
                  <td className="p-3">{p.actividad}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {resultado && resultado.posibles_entregas_sin_corregir.length === 0 && (
        <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          No se detectaron entregas sin corregir en el reporte cargado.
        </p>
      )}
    </Card>
  )
}
