import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Alert } from '@/shared/components/Alert'
import { Combobox } from '@/shared/components/Combobox'
import { useUsuarios } from '@/features/admin/hooks/useAdmin'
import type { FacturaCreate } from '@/features/liquidaciones/types'

interface FacturaFormProps {
  onSave: (payload: FacturaCreate) => Promise<void>
  onCancel: () => void
}

export function FacturaForm({ onSave, onCancel }: FacturaFormProps) {
  const [usuarioId, setUsuarioId] = useState('')
  const [periodo, setPeriodo] = useState('')
  const [detalle, setDetalle] = useState('')
  const [referenciaArchivo, setReferenciaArchivo] = useState('')
  const [archivoSizeBytes, setArchivoSizeBytes] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: usuariosResp, isLoading: loadingUsuarios } = useUsuarios()
  const usuarioItems = (usuariosResp?.items ?? []).map((u) => ({
    value: u.id,
    label: `${u.nombre} ${u.apellidos} (${u.email})`,
  }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (!usuarioId || !periodo.trim() || !detalle.trim() || !referenciaArchivo.trim() || !archivoSizeBytes) {
      setError('Todos los campos son obligatorios.')
      return
    }
    setSaving(true)
    try {
      await onSave({
        usuario_id: usuarioId,
        periodo: periodo.trim(),
        detalle: detalle.trim(),
        referencia_archivo: referenciaArchivo.trim(),
        archivo_size_bytes: Number(archivoSizeBytes),
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
          label="Usuario *"
          items={usuarioItems}
          value={usuarioId}
          onChange={setUsuarioId}
          placeholder="Buscar usuario..."
          isLoading={loadingUsuarios}
        />
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Período * (YYYY-MM)</label>
          <input
            type="text"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            placeholder="ej: 2026-06"
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <label className="block text-sm font-medium text-gray-700">Detalle *</label>
          <input
            type="text"
            value={detalle}
            onChange={(e) => setDetalle(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Referencia de archivo *</label>
          <input
            type="text"
            value={referenciaArchivo}
            onChange={(e) => setReferenciaArchivo(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Tamaño del archivo (bytes) *</label>
          <input
            type="number"
            value={archivoSizeBytes}
            onChange={(e) => setArchivoSizeBytes(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
            min={1}
          />
        </div>
      </div>
      <div className="flex justify-end gap-3">
        <Button variant="secondary" onClick={onCancel} type="button">Cancelar</Button>
        <Button type="submit" loading={saving}>Registrar factura</Button>
      </div>
    </form>
  )
}
