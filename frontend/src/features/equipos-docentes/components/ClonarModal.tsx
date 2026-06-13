import { useState } from 'react'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { Combobox } from '@/shared/components/Combobox'
import { useClonarEquipo } from '@/features/equipos-docentes/hooks/useEquipos'
import { useMaterias } from '@/features/admin/hooks/useAdmin'

interface ClonarModalProps {
  origenEquipoId: string
  onClose: () => void
}

export function ClonarModal({ origenEquipoId, onClose }: ClonarModalProps) {
  const [destinoMateriaId, setDestinoMateriaId] = useState('')
  const [periodo, setPeriodo] = useState('')
  const mutation = useClonarEquipo()

  const { data: materiasResp, isLoading: loadingMaterias } = useMaterias()
  const materiaItems = (materiasResp?.items ?? []).map((m) => ({
    value: m.id,
    label: `${m.nombre} (${m.codigo})${m.carrera_nombre ? ` - ${m.carrera_nombre}` : ''}`,
  }))

  const handleSubmit = async () => {
    if (!destinoMateriaId.trim() || !periodo.trim()) return
    try {
      await mutation.mutateAsync({ origen_equipo_id: origenEquipoId, destino_materia_id: destinoMateriaId, periodo })
      onClose()
    } catch {
      // error handled by mutation
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <Card className="w-full max-w-md p-6" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Clonar Equipo</h2>

        <div className="space-y-4">
          <Combobox
            label="Materia destino"
            items={materiaItems}
            value={destinoMateriaId}
            onChange={setDestinoMateriaId}
            placeholder="Buscar materia destino..."
            isLoading={loadingMaterias}
          />
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Período</label>
            <input
              type="text"
              value={periodo}
              onChange={(e) => setPeriodo(e.target.value)}
              placeholder="Ej: 2026-1"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancelar</Button>
          <Button onClick={handleSubmit} loading={mutation.isPending}>Clonar</Button>
        </div>
      </Card>
    </div>
  )
}
