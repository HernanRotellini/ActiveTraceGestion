import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import type { SalarioBase, SalarioBasePayload } from '@/features/liquidaciones/types'

interface SalarioBaseFormProps {
  salario?: SalarioBase
  onSave: (payload: SalarioBasePayload) => Promise<void>
  onCancel: () => void
}

export function SalarioBaseForm({ salario, onSave, onCancel }: SalarioBaseFormProps) {
  const [rol, setRol] = useState(salario?.rol ?? '')
  const [importe, setImporte] = useState(salario?.importe.toString() ?? '')
  const [vigenciaDesde, setVigenciaDesde] = useState(salario?.vigencia_desde ?? '')
  const [vigenciaHasta, setVigenciaHasta] = useState(salario?.vigencia_hasta ?? '')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!rol.trim() || !importe || !vigenciaDesde) {
      setError('Rol, importe y vigencia desde son obligatorios.')
      return
    }
    setSaving(true)
    try {
      await onSave({
        rol: rol.trim(),
        importe: Number(importe),
        vigencia_desde: vigenciaDesde,
        vigencia_hasta: vigenciaHasta || undefined,
      })
    } catch {
      setError('Error al guardar el salario base.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <Alert variant="error">{error}</Alert>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Rol *</label>
          <input
            type="text"
            value={rol}
            onChange={(e) => setRol(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Importe *</label>
          <input
            type="number"
            value={importe}
            onChange={(e) => setImporte(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
            min={0}
            step="0.01"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Vigencia desde *</label>
          <input
            type="date"
            value={vigenciaDesde}
            onChange={(e) => setVigenciaDesde(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Vigencia hasta</label>
          <input
            type="date"
            value={vigenciaHasta}
            onChange={(e) => setVigenciaHasta(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} type="button">Cancelar</Button>
        <Button type="submit" loading={saving}>{salario ? 'Actualizar' : 'Crear'}</Button>
      </div>
    </form>
  )
}
