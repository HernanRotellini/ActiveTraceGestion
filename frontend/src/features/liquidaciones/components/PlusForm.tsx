import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import type { SalarioPlusCreate, RolLiquidacion } from '@/features/liquidaciones/types'

const ROLES: RolLiquidacion[] = ['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR']

interface PlusFormProps {
  onSave: (payload: SalarioPlusCreate) => Promise<void>
  onCancel: () => void
}

export function PlusForm({ onSave, onCancel }: PlusFormProps) {
  const [rol, setRol] = useState<RolLiquidacion>('PROFESOR')
  const [grupo, setGrupo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [monto, setMonto] = useState('')
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!grupo.trim() || !descripcion.trim() || !monto || !desde) {
      setError('Grupo, descripción, monto y desde son obligatorios.')
      return
    }
    setSaving(true)
    try {
      await onSave({ rol, grupo: grupo.trim(), descripcion: descripcion.trim(), monto, desde, hasta: hasta || undefined })
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
          <label className="block text-sm font-medium text-gray-700">Rol *</label>
          <select
            value={rol}
            onChange={(e) => setRol(e.target.value as RolLiquidacion)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Grupo *</label>
          <input
            type="text"
            value={grupo}
            onChange={(e) => setGrupo(e.target.value)}
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
          <label className="block text-sm font-medium text-gray-700">Monto *</label>
          <input
            type="number"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
            min={0}
            step="0.01"
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Desde *</label>
          <input
            type="date"
            value={desde}
            onChange={(e) => setDesde(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Hasta</label>
          <input
            type="date"
            value={hasta}
            onChange={(e) => setHasta(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} type="button">Cancelar</Button>
        <Button type="submit" loading={saving}>Crear plus</Button>
      </div>
    </form>
  )
}
