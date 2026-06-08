import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import type { Plus, PlusPayload } from '@/features/liquidaciones/types'

interface PlusFormProps {
  plus?: Plus
  onSave: (payload: PlusPayload) => Promise<void>
  onCancel: () => void
}

export function PlusForm({ plus, onSave, onCancel }: PlusFormProps) {
  const [clave, setClave] = useState(plus?.clave ?? '')
  const [rol, setRol] = useState(plus?.rol ?? '')
  const [descripcion, setDescripcion] = useState(plus?.descripcion ?? '')
  const [importe, setImporte] = useState(plus?.importe.toString() ?? '')
  const [vigenciaDesde, setVigenciaDesde] = useState(plus?.vigencia_desde ?? '')
  const [vigenciaHasta, setVigenciaHasta] = useState(plus?.vigencia_hasta ?? '')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!clave.trim() || !rol.trim() || !descripcion.trim() || !importe || !vigenciaDesde) {
      setError('Clave, rol, descripción, importe y vigencia son obligatorios.')
      return
    }
    setSaving(true)
    try {
      await onSave({
        clave: clave.trim(),
        rol: rol.trim(),
        descripcion: descripcion.trim(),
        importe: Number(importe),
        vigencia_desde: vigenciaDesde,
        vigencia_hasta: vigenciaHasta || undefined,
      })
    } catch {
      setError('Error al guardar el plus.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <Alert variant="error">{error}</Alert>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Clave *</label>
          <input
            type="text"
            value={clave}
            onChange={(e) => setClave(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
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
        <div className="space-y-1 sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">Descripción *</label>
          <input
            type="text"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
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
        <Button type="submit" loading={saving}>{plus ? 'Actualizar' : 'Crear'}</Button>
      </div>
    </form>
  )
}
