import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Combobox } from '@/shared/components/Combobox'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { Factura, FacturaPayload } from '@/features/liquidaciones/types'

interface FacturaFormProps {
  factura?: Factura
  onSave: (payload: FacturaPayload) => Promise<void>
  onCancel: () => void
}

export function FacturaForm({ factura, onSave, onCancel }: FacturaFormProps) {
  const [docenteId, setDocenteId] = useState(factura?.docente_id ?? '')
  const [periodo, setPeriodo] = useState(factura?.periodo ?? '')
  const [importe, setImporte] = useState(factura?.importe.toString() ?? '')
  const [observaciones, setObservaciones] = useState(factura?.observaciones ?? '')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} (${u.email})`,
  }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!docenteId.trim() || !periodo.trim() || !importe) {
      setError('Docente, período e importe son obligatorios.')
      return
    }
    setSaving(true)
    try {
      await onSave({
        docente_id: docenteId.trim(),
        periodo: periodo.trim(),
        importe: Number(importe),
        observaciones: observaciones.trim() || undefined,
      })
    } catch {
      setError('Error al guardar la factura.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <Alert variant="error">{error}</Alert>}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Combobox
          label="Docente *"
          items={usuarioItems}
          value={docenteId}
          onChange={setDocenteId}
          placeholder="Buscar docente..."
          isLoading={loadingUsuarios}
        />
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Período *</label>
          <input
            type="text"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            placeholder="ej: 2026-06"
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
          <label className="block text-sm font-medium text-gray-700">Observaciones</label>
          <input
            type="text"
            value={observaciones}
            onChange={(e) => setObservaciones(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} type="button">Cancelar</Button>
        <Button type="submit" loading={saving}>Crear factura</Button>
      </div>
    </form>
  )
}
